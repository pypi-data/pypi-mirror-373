import inspect
from dataclasses import is_dataclass
from typing import Any

from msgspec import json
from pydantic import BaseModel


def extract_openapi_schema(cls: Any) -> dict[str, Any]:
    """Extract the OpenAPI-compatible JSON schema of a Pydantic model or dataclass if applicable."""
    if issubclass(cls, BaseModel):
        schema = cls.model_json_schema()
        # Get all properties and preserve their descriptions
        properties = schema.get("properties", {})

        # Determine required fields - use the required list from the schema
        required = schema.get("required", [])

        return {
            "type": "object",
            "properties": properties,
            "required": required,
            "title": schema.get("title", cls.__name__),
            "description": schema.get("description", ""),
        }
    if is_dataclass(cls):
        # Generate JSON schema using msgspec
        schema = json.schema(cls)
        properties = (
            schema.get("$defs", {})
            .get(cls.__name__, {})
            .get("properties", {})
        )

        # Determine required fields for dataclasses
        required = [
            name
            for name, prop in properties.items()
            if not any(
                subschema.get("type") == "null"
                for subschema in prop.get("anyOf", [])
            )
        ]

        new_properties = {}
        for prop_name, prop_schema in properties.items():
            new_prop_schema = prop_schema
            if "description" in prop_schema:
                new_prop_schema = {
                    **prop_schema,
                    "description": prop_schema["description"],
                }
            new_properties[prop_name] = new_prop_schema

        return {
            "type": "object",
            "properties": new_properties,
            "required": required,
            "title": cls.__name__,
        }
    return {}


def explore_class_details(cls: Any) -> dict[str, Any]:
    """Extract detailed information about a class or function, focusing on input/output schemas.

    Returns:
        Dict containing:
        - name: The name of the class/function
        - type: 'class' or 'function'
        - input_schema: OpenAPI-compatible JSON schema of the input if applicable
        - output_schema: OpenAPI-compatible JSON schema of the output if applicable

    """
    details = {
        "name": getattr(cls, "__name__", "Unknown"),
        "type": "class" if inspect.isclass(cls) else "function",
        "input_schema": {},
        "output_schema": {},
        "description": (
            getattr(cls, "__restack_description__", "")
        ),
    }

    if inspect.isclass(cls):
        for name, method in inspect.getmembers(
            cls,
            predicate=inspect.isfunction,
        ):
            if name == "run":
                sig = inspect.signature(method)
                for param in sig.parameters.values():
                    if (
                        param.annotation
                        != inspect.Parameter.empty
                        and inspect.isclass(
                            param.annotation,
                        )
                    ):
                        details["input_schema"] = (
                            extract_openapi_schema(
                                param.annotation,
                            )
                        )
                if (
                    sig.return_annotation
                    != inspect.Signature.empty
                    and inspect.isclass(
                        sig.return_annotation,
                    )
                ):
                    details["output_schema"] = (
                        extract_openapi_schema(
                            sig.return_annotation,
                        )
                    )

    return details
