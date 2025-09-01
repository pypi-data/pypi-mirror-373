from .schema import BaseSchemaExtractor as BaseSchemaExtractor
from inspect import Parameter
from typing import Any

class FastApiSchemaExtractor(BaseSchemaExtractor):
    """FastAPI-specific schema extractor implementation."""
    def get_type_schema(self, type_: type) -> dict[str, Any]:
        """Convert a Python type to a JSON Schema."""
    def get_param_constraints(self, param: Parameter) -> dict[str, Any]:
        """Extract parameter constraints from FastAPI parameter."""
