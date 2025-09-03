import uuid
from typing import Any, Tuple, Iterable

from bson.objectid import ObjectId as BsonObjectId, InvalidId
from fastapi import Depends, Query, Request
from fastapi.exceptions import RequestValidationError
from pydantic import (
    GetCoreSchemaHandler,
    GetJsonSchemaHandler,
    ValidationError,
    create_model,
    BaseModel,
    Field,
)
from pydantic.types import JsonSchemaValue
from pydantic_core import CoreSchema, core_schema


class ObjectId(str):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_before_validator_function(
            cls.validate_objectid_string, handler(str)
        )

    @classmethod
    def validate_objectid_string(cls, v: Any) -> str:
        try:
            if v is None:
                raise InvalidId(
                    "None is not a valid ObjectId, it must be a 12-byte input or a 24-character hex string"
                )
            return str(BsonObjectId(v))
        except InvalidId as e:
            raise ValueError(str(e))

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        json_schema = handler(core_schema)
        json_schema = handler.resolve_ref_schema(json_schema)

        json_schema["type"] = "string"
        json_schema["min_length"] = 24
        json_schema["max_length"] = 24
        json_schema["pattern"] = "^[0-9a-fA-F]{24}$"
        json_schema["regex_engine"] = "python-re"
        json_schema["examples"] = ["5ba3b37eb6fa1e372f53d04c"]
        return json_schema


class UUID(str):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_before_validator_function(
            cls.validate_uuid_string, handler(str)
        )

    @classmethod
    def validate_uuid_string(cls, v: Any) -> str:
        return str(uuid.UUID(v))

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        json_schema = handler(core_schema)
        json_schema = handler.resolve_ref_schema(json_schema)

        json_schema["type"] = "string"
        json_schema["min_length"] = 36
        json_schema["max_length"] = 36
        json_schema["pattern"] = (
            "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
        )
        json_schema["regex_engine"] = "python-re"
        json_schema["examples"] = ["ec8ccc64-81dc-4b7b-a72e-daa7172bfae6"]
        return json_schema


def LimitOffset(limit_default=20, limit_max=300):  # noqa: N802
    @Depends
    async def get_limit_offset(
        limit: int = Query(
            default=limit_default,
            ge=0,
            le=limit_max,
            description="The maximum number of entries to be returned per call",
            example=limit_default,
        ),
        offset: int = Query(
            default=0,
            ge=0,
            description="The (zero-based) offset of the first item returned in the collection",  # noqa: E501
            example=0,
        ),
    ) -> Tuple[int, int]:
        return limit, offset

    return get_limit_offset


def subfields(field_name: str, field_type: type, subfields: Iterable[str], **kwargs):
    root_field = {"": (field_type, Field(alias=field_name, **kwargs))}

    # Model with root field for the schema definition
    field_model = create_model("FieldModel", **root_field)

    # Model with all fields for parsing
    subfields_model: BaseModel = create_model(
        "SubfieldsModel",
        **root_field,
        **{
            subfield: (field_type, Field(alias=f"{field_name}[{subfield}]", **kwargs))
            for subfield in subfields
        },
    )

    async def parse_subfields(request: Request, root_field: field_model = Depends()):
        try:
            return subfields_model.model_validate(request.query_params).model_dump(
                exclude_none=True
            )
        except ValidationError as error:
            raise RequestValidationError(repr(error.errors()))

    return Depends(parse_subfields)
