import abc
from abc import ABC, abstractmethod
from inspect import Parameter
from typing import Any, Callable

class SchemaExtractor(ABC, metaclass=abc.ABCMeta):
    """Base class for framework-specific schema extraction."""
    @abstractmethod
    def get_type_schema(self, type_: type) -> dict[str, Any]:
        """Convert a Python type to a JSON Schema.

        Args:
            type_: The Python type to convert

        Returns:
            JSON Schema representation of the type
        """
    @abstractmethod
    def get_param_constraints(self, param: Parameter) -> dict[str, Any]:
        """Extract parameter constraints from a parameter.

        Args:
            param: The parameter to extract constraints from

        Returns:
            Dictionary of parameter constraints
        """
    @abstractmethod
    def get_route_parameters(self, handler: Callable) -> dict[str, Any]:
        """Extract route parameter information from a handler function.

        Args:
            handler: The route handler function

        Returns:
            Dictionary of parameter information
        """
    @abstractmethod
    def get_request_body(self, handler: Callable) -> dict[str, Any] | None:
        """Extract request body schema from a handler function.

        Args:
            handler: The route handler function

        Returns:
            Request body schema if present, None otherwise
        """
    @abstractmethod
    def get_response_schema(self, handler: Callable) -> dict[str, Any]:
        """Extract response schema from a handler function.

        Args:
            handler: The route handler function

        Returns:
            Response schema
        """

class BaseSchemaExtractor(SchemaExtractor):
    """Base implementation of schema extraction with common functionality."""
    def get_type_schema(self, type_: type) -> dict[str, Any]:
        """Convert a Python type to a JSON Schema."""
    def get_param_constraints(self, param: Parameter) -> dict[str, Any]:
        """Extract parameter constraints from a parameter.

        Args:
            param: The parameter to extract constraints from

        Returns:
            Dictionary of parameter constraints
        """
    def get_route_parameters(self, handler: Callable) -> dict[str, Any]:
        """Extract route parameter information from a handler function."""
    def get_request_body(self, handler: Callable) -> dict[str, Any] | None:
        """Extract request body schema from a handler function."""
    def get_response_schema(self, handler: Callable) -> dict[str, Any]:
        """Extract response schema from a handler function."""
