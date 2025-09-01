from pydantic import GetCoreSchemaHandler as GetCoreSchemaHandler, GetJsonSchemaHandler as GetJsonSchemaHandler
from pydantic_core import core_schema
from starlette.datastructures import UploadFile
from typing import Any, Callable

class InputFile(UploadFile):
    """A version of Starlette's UploadFile that can be used as a Pydantic field type.

    This allows for file uploads to be properly validated in Pydantic models
    while preserving all the functionality of Starlette's UploadFile.
    """
    @classmethod
    def __get_validators__(cls) -> list[Callable]:
        """Return validators for Pydantic v1 compatibility."""
    @classmethod
    def validate(cls, value: Any) -> InputFile:
        """Validate an input value and convert to UploadFile."""
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type: Any, _handler: GetCoreSchemaHandler) -> Any:
        """Get Pydantic core schema for Pydantic v2 compatibility."""
    @classmethod
    def __get_pydantic_json_schema__(cls, _core_schema: core_schema.CoreSchema, _handler: GetJsonSchemaHandler) -> dict[str, Any]:
        """Define JSON schema for InputFile type."""
