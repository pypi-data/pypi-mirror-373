import json
import types
from pathlib import Path

import PIL.Image
import structlog
from beartype.typing import Any, Union, get_args, get_origin

from superlinked.framework.common.schema.event_schema_object import SchemaReference
from superlinked.framework.common.schema.id_field import IdField
from superlinked.framework.common.schema.schema import IdSchemaObject
from superlinked.framework.common.schema.schema_object import (
    Blob,
    Boolean,
    Float,
    FloatList,
    Integer,
    String,
    StringList,
    Timestamp,
)
from superlinked.framework.dsl.query.query_descriptor import QueryDescriptor
from superlinked.framework.dsl.query.typed_param import TypedParam

logger = structlog.getLogger(__name__)

INGEST_ENDPOINT_DESCRIPTOR_PATH = "openapi/ingest_endpoint_descriptor.json"
QUERY_ENDPOINT_DESCRIPTOR_PATH = "openapi/query_endpoint_descriptor.json"


class OpenApiSchemaGenerator:
    _TYPE_MAP: dict[Any, dict[str, Any]] = {
        # Superlinked Ingest Types
        IdField: {"type": "string", "example": "my-unique-id-123"},
        String: {"type": "string", "example": "some-sample-string-value"},
        Timestamp: {"type": "integer", "format": "int64", "example": 1704067200},
        Float: {"type": "number", "format": "float", "example": 123.45},
        Integer: {"type": "integer", "example": 100},
        Boolean: {"type": "boolean", "example": True},
        FloatList: {"type": "array", "items": {"type": "number", "format": "float"}, "example": [1.0, 0.5, 0.0]},
        StringList: {"type": "array", "items": {"type": "string"}, "example": ["item_1", "item_2"]},
        Blob: {"type": "string", "format": "uri", "example": "https://example.com/blob"},
        SchemaReference: {"type": "string", "example": "affected-object-id-123"},
        # Python Query Primitives
        str: {"type": "string", "example": "sample-string"},
        int: {"type": "integer", "example": 42},
        float: {"type": "number", "format": "float", "example": 3.14},
        bool: {"type": "boolean", "example": True},
        dict: {"type": "object", "example": {"key": "value"}},
    }

    @staticmethod
    def generate_ingest_spec(schema: IdSchemaObject) -> dict[str, Any]:
        return {
            "summary": f"Ingest data for {schema._schema_name}",
            "requestBody": {
                "content": {"application/json": {"schema": OpenApiSchemaGenerator._build_ingest_schema(schema)}}
            },
            **OpenApiSchemaGenerator._get_open_api_description_by_key(INGEST_ENDPOINT_DESCRIPTOR_PATH),
        }

    @staticmethod
    def generate_query_spec(query_descriptor: QueryDescriptor) -> dict[str, Any]:
        return {
            "summary": f"Query for {query_descriptor.schema._schema_name}",
            "requestBody": {
                "content": {
                    "application/json": {"schema": OpenApiSchemaGenerator._build_query_schema(query_descriptor)}
                }
            },
            **OpenApiSchemaGenerator._get_open_api_description_by_key(QUERY_ENDPOINT_DESCRIPTOR_PATH),
        }

    @staticmethod
    def _build_ingest_schema(schema: IdSchemaObject) -> dict[str, Any]:
        properties: dict[str, Any] = {}
        required: list[str] = []

        schema_property = OpenApiSchemaGenerator._map_type_to_schema(IdField)
        schema_property["description"] = "Unique identifier for the object."
        properties[schema.id.name] = schema_property
        required.append(schema.id.name)

        for name, type_ in schema._schema_fields_by_name.items():
            properties[name] = OpenApiSchemaGenerator._map_type_to_schema(type(type_))
            if not type_.nullable:
                required.append(name)

        return {"type": "object", "properties": properties, "required": required}

    @staticmethod
    def _build_query_schema(query_descriptor: QueryDescriptor) -> dict[str, Any]:
        properties: dict[str, Any] = {}
        for param in OpenApiSchemaGenerator._get_typed_params(query_descriptor):
            possible_types = [types_.original_type for types_ in param.valid_param_value_types]
            if not possible_types:
                continue

            param_type_hint = Union[tuple(possible_types)] if len(possible_types) > 1 else possible_types[0]

            schema = OpenApiSchemaGenerator._map_type_to_schema(param_type_hint)
            schema["description"] = f"Parameter '{param.param.name}'."
            properties[param.param.name] = schema

        return {"type": "object", "properties": properties, "required": []}

    @staticmethod
    def _map_type_to_schema(type_hint: Any) -> dict[str, Any]:
        origin = get_origin(type_hint)
        args = get_args(type_hint)

        if origin is Union or origin is types.UnionType:
            sub_schemas = [OpenApiSchemaGenerator._map_type_to_schema(arg) for arg in args if arg is not type(None)]
            return {"anyOf": sub_schemas} if len(sub_schemas) > 1 else (sub_schemas[0] if sub_schemas else {})

        if origin is list:
            item_schema = OpenApiSchemaGenerator._map_type_to_schema(args[0]) if args else {}
            return {"type": "array", "items": item_schema}

        if type_hint in OpenApiSchemaGenerator._TYPE_MAP:
            return OpenApiSchemaGenerator._TYPE_MAP[type_hint].copy()

        # PIL.Image.Image is not supported with HTTP so we return an empty schema
        if type_hint == PIL.Image.Image:
            return {}

        logger.warning("Unsupported type in schema generation.", field_type=str(type_hint))
        return {"type": "object", "description": f"Unsupported type: {type_hint}"}

    @staticmethod
    def _get_typed_params(query_descriptor: QueryDescriptor) -> list[TypedParam]:
        return [
            param for clause in query_descriptor.clauses for param in clause.params if isinstance(param, TypedParam)
        ]

    @staticmethod
    def _get_open_api_description_by_key(file_path: str) -> dict[str, Any]:
        full_path = Path(__file__).parent.parent / file_path
        with open(full_path, encoding="utf-8") as file:
            return json.load(file)
