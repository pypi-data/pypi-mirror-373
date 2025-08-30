from typing import Any

import websockets
from temporalio import activity
from temporalio.exceptions import ApplicationError

from .observability import log_with_context, logger

activity.logger.logger = logger


class ActivityLogger:
    """Enables consistent formatting for function logs."""

    def __init__(self) -> None:
        self._logger = activity.logger

    def _log(
        self,
        level: str,
        message: str,
        **kwargs: Any,
    ) -> None:
        try:
            activity.info()
            getattr(self._logger, level)(
                message,
                extra={
                    "extra_fields": {
                        **kwargs,
                        "client_log": True,
                    },
                },
            )
        except RuntimeError:
            log_with_context(level.upper(), message, **kwargs)

    def debug(self, message: str, **kwargs: Any) -> None:
        self._log("debug", message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        self._log("info", message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        self._log("warning", message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        self._log("error", message, **kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:
        self._log("critical", message, **kwargs)

    def exception(self, message: str, **kwargs: Any) -> None:
        """Log an exception with traceback (equivalent to `logging.exception`)."""
        kwargs["exc_info"] = True
        self._log("exception", message, **kwargs)


log = ActivityLogger()

function_info = activity.info
heartbeat = activity.heartbeat
function = activity


class NonRetryableError(ApplicationError):
    def __init__(self, message: str) -> None:
        super().__init__(message=message, non_retryable=True)


class RetryableError(ApplicationError):
    def __init__(self, message: str) -> None:
        super().__init__(message=message, non_retryable=False)


__all__ = [
    "NonRetryableError",
    "RetryableError",
    "function_info",
    "heartbeat",
    "log",
    "mcp_progress",
]


def mcp_progress(
    progress: float,
    total: float | None = None,
    message: str | None = None,
) -> bool:
    """Send an MCP-compliant progress information.

    Example:

    .. code-block:: python

        # Basic progress
        mcp_progress(progress=25, total=100, message="Loading data")

        # Progress update
        mcp_progress(progress=50, total=100, message="Processing data")

    Args:
        progress (float): Current progress value (must increase with each call)
        total (float, optional): Total progress value if known
        message (str, optional): Human-readable progress message

    Returns:
        bool: True if the progress information was sent successfully, False otherwise

    """
    try:
        info = activity.info()

        mcp_data = {
            "_mcp_progress": True,
            "progress": float(progress),
            "activity_id": info.activity_id,
            "activity_type": info.activity_type,
        }

        # Add optional fields
        if total is not None:
            mcp_data["total"] = float(total)

        if message is not None:
            mcp_data["message"] = str(message)

        heartbeat(mcp_data)

    except Exception:
        log.exception("Error sending MCP progress")
        return False
    else:
        return True


def current_workflow() -> Any:
    return activity.Context.current().info


def _extract_response_info(
    chunk: Any,
) -> tuple[Any, str | None, Any, bool]:
    """Extract response information from a chunk.

    Returns:
        tuple: (final_response, response_id, usage_info, has_completion)
    """
    final_response = None
    response_id = None
    usage_info = None
    has_completion = False

    # Extract final response from completion events
    if hasattr(chunk, "response") and chunk.response:
        final_response = chunk.response
        if hasattr(chunk.response, "id"):
            response_id = chunk.response.id
        has_completion = True

        # Extract usage information
        if (
            hasattr(chunk.response, "usage")
            and chunk.response.usage
        ):
            usage_info = chunk.response.usage

    # Extract usage from standalone usage events
    elif hasattr(chunk, "usage") and chunk.usage:
        usage_info = chunk.usage

    # Check for completion based on OpenAI responses API event types
    if hasattr(chunk, "type"):
        chunk_type = chunk.type
        has_completion = _check_completion_type(chunk_type)

        # Also check if this is the main response object with complete data
        if (
            chunk_type == "response"
            and hasattr(chunk, "status")
            and chunk.status
            in ["completed", "failed", "incomplete"]
        ):
            has_completion = True
            final_response = chunk
            if hasattr(chunk, "id"):
                response_id = chunk.id
            if hasattr(chunk, "usage"):
                usage_info = chunk.usage

    return final_response, response_id, usage_info, has_completion


def _check_completion_type(chunk_type: str) -> bool:
    """Check if chunk type indicates completion.

    Returns:
        bool: True if chunk_type indicates final completion
    """
    # Only set has_completion=True for final completion events that indicate the entire response is done
    final_completion_types = [
        "response.completed",  # Main response completion
        "response.failed",  # Response failed
        "response.incomplete",  # Response cut off (max_tokens, etc)
        "response.done",  # Legacy completion event
    ]

    # Item-level completion events indicate partial completion but NOT final completion
    # These should NOT set has_completion=True as they don't mean the entire response is done
    partial_completion_types = [
        "response.output_text.done",  # Text output completed
        "response.output_item.done",  # Output item completed
        "response.content_part.done",  # Content part completed
        "response.mcp_call.completed",  # MCP tool call completed
        "response.mcp_call.failed",  # MCP tool call failed
        "response.function_call_arguments.done",  # Function call args completed
        "response.refusal.done",  # Refusal completed
        "response.reasoning_text.done",  # Reasoning completed
        "response.file_search_call.completed",  # File search completed
        "response.web_search_call.completed",  # Web search completed
        "response.code_interpreter_call.completed",  # Code interpreter completed
        "response.image_generation_call.completed",  # Image generation completed
    ]

    if chunk_type in final_completion_types:
        return True
    if chunk_type in partial_completion_types:
        # These indicate partial completion but don't necessarily mean the entire response is done
        # Do NOT set has_completion=True for these partial events
        return False

    return False


def _build_websocket_url(
    api_address: str,
    workflow_id: str,
    run_id: str,
) -> str:
    """Build the WebSocket URL for streaming.

    Returns:
        str: The WebSocket URL
    """
    protocol = (
        "ws" if api_address.startswith("localhost") else "wss"
    )
    return f"{protocol}://{api_address}/stream/ws/agent?agentId={workflow_id}&runId={run_id}"


def _get_activity_info() -> dict:
    """Get current activity information.

    Returns:
        dict: Activity information
    """
    return {
        "activityId": activity.info().activity_id,
        "workflowId": activity.info().workflow_id,
        "runId": activity.info().workflow_run_id,
        "activityType": activity.info().activity_type,
        "taskQueue": activity.info().task_queue,
    }


class StreamState:
    """Holds accumulated stream processing state."""

    def __init__(self) -> None:
        self.final_response = None
        self.response_id: str | None = None
        self.usage_info = None
        self.has_completion = False


async def _process_chunk(
    chunk: Any,
    websocket: Any,
    collected_events: list,
    state: StreamState,
) -> None:
    """Process a single chunk and update accumulated data.

    Strategy: Forward all streaming events as-is to the frontend via websocket,
    while collecting completion states and final response data for return value.

    Args:
        chunk: The chunk to process
        websocket: WebSocket connection
        collected_events: List to append events to
        state: Stream processing state to update
    """
    raw_chunk_json = chunk.model_dump_json()
    heartbeat(raw_chunk_json)

    # Forward the streaming event as-is to frontend
    if websocket.state.name in ["OPEN", "CONNECTING"]:
        await websocket.send(message=raw_chunk_json)

    chunk_dict = chunk.model_dump()
    collected_events.append(chunk_dict)

    # Extract response information from chunk
    (
        chunk_final_response,
        chunk_response_id,
        chunk_usage_info,
        chunk_has_completion,
    ) = _extract_response_info(chunk)

    # Update accumulated data
    state.final_response = (
        chunk_final_response or state.final_response
    )
    state.response_id = chunk_response_id or state.response_id
    state.usage_info = chunk_usage_info or state.usage_info
    state.has_completion = (
        state.has_completion or chunk_has_completion
    )


async def _iterate_stream(
    data: Any,
    websocket: Any,
    collected_events: list,
) -> StreamState:
    """Iterate through stream data (async or sync) and process chunks.

    Returns:
        StreamState: The accumulated stream processing state
    """
    state = StreamState()

    try:
        if hasattr(data, "__aiter__"):
            # Async iteration
            async for chunk in data:
                await _process_chunk(
                    chunk,
                    websocket,
                    collected_events,
                    state,
                )
        else:
            # Sync iteration
            for chunk in data:
                await _process_chunk(
                    chunk,
                    websocket,
                    collected_events,
                    state,
                )
    except (
        AttributeError,
        KeyError,
        TypeError,
        ValueError,
        RuntimeError,
    ) as stream_error:
        log.warning(
            "Error during stream processing",
            error=str(stream_error),
        )

    return state


async def _process_openai_stream(
    data: Any,
    websocket: Any,
) -> dict:
    """Process OpenAI stream data and send to WebSocket.

    Returns:
        dict: Collected data including events, text, and metadata
    """
    log.info("Processing OpenAI stream", data=data)

    collected_events = []
    state = await _iterate_stream(
        data,
        websocket,
        collected_events,
    )

    return {
        "events": collected_events,
        "text": "",
        "final_response": state.final_response,
        "response_id": state.response_id,
        "usage": state.usage_info,
        "has_completion": state.has_completion,
    }


async def stream_to_websocket(
    api_address: str | None = None,
    data: Any = None,
) -> Any:
    """Stream data to Restack Engine WebSocket API endpoint.

    This function streams data to the Restack Engine and returns a comprehensive result
    with collected events, concatenated text, and metadata. It handles both simple text
    extraction and full response aggregation in a single, robust implementation.

    Args:
        api_address (str): The address of the Restack Engine API.
        data (Any): The streamed data from an OpenAI-compatible API or a JSON dict.

    Returns:
        dict: A dictionary containing:
            - events: List of all collected events (raw chunks)
            - event_count: Number of events collected
            - final_response: Complete aggregated response (if available)
            - response_id: Response ID if available
            - usage: Usage statistics if available
            - has_completion: Whether a completion event was received

    Example:
        >>> from openai import OpenAI
        >>> client = OpenAI()
        >>> # Stream a response
        >>> stream = client.responses.create(
        ...     model="gpt-4o", input="Hello, how are you?", stream=True
        ... )
        >>> # Stream to websocket and get comprehensive result
        >>> result = await stream_to_websocket(data=stream)
        >>> # Access the concatenated text
        >>> print(result["text"])
        >>> # Access the complete reconstructed response
        >>> if result["final_response"]:
        ...     print(f"Complete response: {result['final_response']}")
        >>> # Access metadata
        >>> print(f"Response ID: {result['response_id']}")
        >>> print(f"Usage: {result['usage']}")
    """
    if api_address is None:
        api_address = "localhost:9233"

    info = _get_activity_info()
    websocket_url = _build_websocket_url(
        api_address,
        info["workflowId"],
        info["runId"],
    )

    try:
        async with websockets.connect(websocket_url) as websocket:
            try:
                heartbeat(info)

                log.info("Sending heartbeat", info=info)

                log.info("data", data=data)

                # Check if module name is openai (no need to import openai package in this library)
                if data.__class__.__module__.startswith("openai"):
                    log.info(
                        "Processing OpenAI stream",
                        data=data,
                    )

                    result = await _process_openai_stream(
                        data,
                        websocket,
                    )

                else:
                    log.info(
                        "Processing non-OpenAI stream",
                        data=data,
                    )

                    # Handle non-OpenAI data (placeholder for future implementation)
                    result = {
                        "events": [],
                        "text": "",
                        "final_response": None,
                        "response_id": None,
                        "usage": None,
                        "has_completion": False,
                    }
            finally:
                # Ensure the WebSocket connection is closed gracefully
                try:
                    if websocket.state.name in [
                        "OPEN",
                        "CONNECTING",
                    ]:
                        await websocket.send(message="[DONE]")
                        await websocket.close()
                except (
                    websockets.exceptions.ConnectionClosed,
                    websockets.exceptions.WebSocketException,
                    RuntimeError,
                    OSError,
                ) as close_error:
                    log.warning(
                        "Error closing WebSocket connection",
                        error=str(close_error),
                    )

            # Validate streaming completed successfully
            if not result["has_completion"]:
                log.warning(
                    "Streaming completed without final response event",
                )

            return {
                "events": result["events"],
                "text": result["text"],
                "event_count": len(result["events"]),
                "final_response": result["final_response"],
                "response_id": result["response_id"],
                "usage": result["usage"],
                "has_completion": result["has_completion"],
            }
    except Exception as e:
        error_message = (
            f"Error with restack stream to websocket: {e}"
        )
        log.exception(error_message)
        raise ApplicationError(error_message) from e
