import asyncio
import base64
import hashlib
import json
from collections.abc import Sequence
from urllib.parse import urlencode

import aiohttp
from temporalio.api.common.v1 import Payload
from temporalio.converter import PayloadCodec

HTTP_OK = 200
HTTP_OK_201 = 201
HTTP_SUCCESS_CODES = {HTTP_OK, HTTP_OK_201}


class LargePayloadCodec(PayloadCodec):
    """Large Payload Codec for Temporal workflows that automatically handles payloads larger than 128KB.

    This codec integrates with the DataDog temporal-large-payload-codec server to store large payloads
    in external blob storage (GCS, S3, or in-memory) instead of keeping them in the workflow history.

    When a payload exceeds 128KB, this codec:
    1. Calculates a SHA-256 digest of the payload data
    2. Uploads the data to the payload codec server
    3. Replaces the original payload with a small reference containing metadata, size, digest, and storage key

    During decoding, it retrieves the original data from storage and restores the complete payload.

    @see https://github.com/DataDog/temporal-large-payload-codec
    """

    def __init__(
        self,
        codec_server_url: str,
        namespace: str,
    ) -> None:
        self.codec_server_url = codec_server_url
        self.namespace = namespace

    def _calculate_digest(self, data: bytes) -> str:
        """Calculate SHA-256 digest of the data."""
        hash_obj = hashlib.sha256(data)
        return f"sha256:{hash_obj.hexdigest()}"

    def _convert_metadata_to_base64(
        self,
        payload: Payload,
    ) -> dict[str, str]:
        """Convert payload metadata to base64 format for Go server compatibility."""
        metadata_for_go: dict[str, str] = {}
        if payload.metadata:
            for key, value in payload.metadata.items():
                if isinstance(value, bytes):
                    metadata_for_go[key] = base64.b64encode(
                        value,
                    ).decode("utf-8")
                else:
                    metadata_for_go[key] = str(value)
        return metadata_for_go

    def _serialize_metadata(
        self,
        payload: Payload,
    ) -> dict[str, str]:
        """Serialize payload metadata for JSON storage."""
        serializable_metadata: dict[str, str] = {}
        if payload.metadata:
            for key, value in payload.metadata.items():
                if isinstance(value, bytes):
                    serializable_metadata[key] = value.decode(
                        "utf-8",
                        errors="ignore",
                    )
                else:
                    serializable_metadata[key] = str(value)
        return serializable_metadata

    async def encode(
        self,
        payloads: Sequence[Payload],
    ) -> list[Payload]:
        """Encode payloads, storing large ones in external storage."""
        if not self.codec_server_url:
            return list(payloads)

        encoded_payloads: list[Payload] = []

        async with aiohttp.ClientSession() as session:
            for payload in payloads:
                payload_size = (
                    len(payload.data) if payload.data else 0
                )
                if payload_size < 128 * 1024:
                    encoded_payloads.append(payload)
                    continue

                try:
                    result = await self._upload_single_payload(
                        session,
                        payload,
                        payload_size,
                    )
                    encoded_payloads.append(result)
                except (
                    aiohttp.ClientError,
                    asyncio.TimeoutError,
                ):
                    encoded_payloads.append(payload)
                except Exception:  # noqa: BLE001
                    encoded_payloads.append(payload)

        return encoded_payloads

    async def _upload_single_payload(
        self,
        session: aiohttp.ClientSession,
        payload: Payload,
        payload_size: int,
    ) -> Payload:
        """Upload a single payload with proper error handling."""
        digest = self._calculate_digest(payload.data)
        metadata_for_go = self._convert_metadata_to_base64(
            payload,
        )

        url = f"{self.codec_server_url}/v2/blobs/put"
        params = {"digest": digest, "namespace": self.namespace}
        url_with_params = f"{url}?{urlencode(params)}"

        headers = {
            "Content-Type": "application/octet-stream",
            "X-Temporal-Metadata": base64.b64encode(
                json.dumps(metadata_for_go).encode("utf-8"),
            ).decode("utf-8"),
        }

        async with session.put(
            url_with_params,
            headers=headers,
            data=payload.data,
        ) as response:
            if response.status in HTTP_SUCCESS_CODES:
                response_text = await response.text()
                key_response = json.loads(response_text)
                serializable_metadata = self._serialize_metadata(
                    payload,
                )

                encoded_data = {
                    "metadata": serializable_metadata,
                    "size": payload_size,
                    "digest": digest,
                    "key": key_response["Key"],
                }

                new_metadata = (
                    dict(payload.metadata)
                    if payload.metadata
                    else {}
                )
                new_metadata["temporal.io/remote-codec"] = b"v2"

                return Payload(
                    metadata=new_metadata,
                    data=json.dumps(encoded_data).encode("utf-8"),
                )

            error_message = "Upload failed"
            raise Exception(error_message)

    async def decode(
        self,
        payloads: Sequence[Payload],
    ) -> list[Payload]:
        """Decode payloads, retrieving large ones from external storage."""
        if not self.codec_server_url:
            return list(payloads)

        decoded_payloads: list[Payload] = []

        async with aiohttp.ClientSession() as session:
            for payload in payloads:
                remote_codec = (
                    payload.metadata.get(
                        "temporal.io/remote-codec",
                    )
                    if payload.metadata
                    else None
                )
                if remote_codec == b"v2":
                    try:
                        encoded_data = payload.data.decode(
                            "utf-8",
                        )
                        decoded_info = json.loads(encoded_data)
                        key = decoded_info["key"]
                        size = decoded_info["size"]
                        url = f"{self.codec_server_url}/v2/blobs/get"
                        params = {"key": key}
                        url_with_params = (
                            f"{url}?{urlencode(params)}"
                        )
                        headers = {
                            "Content-Type": "application/octet-stream",
                            "X-Payload-Expected-Content-Length": str(
                                size,
                            ),
                        }

                        async with session.get(
                            url_with_params,
                            headers=headers,
                        ) as response:
                            if (
                                response.status
                                in HTTP_SUCCESS_CODES
                            ):
                                data = await response.read()
                                decoded_payload = Payload(
                                    metadata=payload.metadata,
                                    data=data,
                                )

                                decoded_payloads.append(
                                    decoded_payload,
                                )
                            else:
                                decoded_payloads.append(payload)

                    except Exception:  # noqa: BLE001
                        decoded_payloads.append(payload)
                else:
                    decoded_payloads.append(payload)
        return decoded_payloads
