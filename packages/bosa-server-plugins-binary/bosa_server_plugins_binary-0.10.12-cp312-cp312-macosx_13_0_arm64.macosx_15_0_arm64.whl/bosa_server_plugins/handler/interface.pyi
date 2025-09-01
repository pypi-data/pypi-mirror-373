import abc
from .auth.schema import AuthenticationSchema as AuthenticationSchema
from .model import BaseRequestModel as BaseRequestModel
from .response import ApiResponse as ApiResponse
from .router import Router as Router
from .schema import SchemaExtractor as SchemaExtractor
from abc import ABC, abstractmethod
from bosa_core.plugin.handler import PluginHandler
from bosa_core.plugin.plugin import Plugin as Plugin
from starlette.responses import RedirectResponse
from typing import Any

class HttpHandler(PluginHandler, ABC, metaclass=abc.ABCMeta):
    """Base interface for HTTP server implementations."""
    base_api_prefix: str
    authentication_schema: AuthenticationSchema | None
    def __init__(self, base_api_prefix: str = '/api', authentication_schema: AuthenticationSchema = None) -> None:
        '''Constructor.

        Args:
            base_api_prefix (str, optional): The base API prefix. Defaults to "/api".
            authentication_schema (AuthenticationSchema, optional): The authentication schema. Defaults to None.
        '''
    @classmethod
    def create_injections(cls, instance: HttpHandler) -> dict[type, Any]:
        """Create injection mappings for HTTP functionality.

        Args:
            instance: The HTTP interface instance

        Returns:
            Dictionary mapping service types to their instances
        """
    @classmethod
    def initialize_plugin(cls, instance: HttpHandler, plugin: Plugin) -> None:
        """Initialize HTTP-specific resources for the plugin.

        If the plugin has a router attribute, register its routes with the HTTP interface.

        Args:
            instance: The HTTP interface instance
            plugin: The plugin instance to initialize
        """
    @abstractmethod
    def get_schema_extractor(self) -> SchemaExtractor:
        """Get the schema extractor for this interface.

        Returns:
            SchemaExtractor implementation for this interface
        """
    @abstractmethod
    def handle_routing(self, prefix: str, router: Router):
        """Register routes with the HTTP interface.

        Args:
            prefix: The prefix for the routes
            router: The router instance
        """
    def redirect(self, url: str, status_code: int = 302) -> RedirectResponse:
        """Create a redirect response.

        Args:
            url: The URL to redirect to
            status_code: HTTP status code for the redirect (defaults to 302 FOUND)

        Returns:
            Starlette RedirectResponse
        """
    def get_plugin_routes(self, plugin: Plugin) -> list[dict[str, Any]]:
        """Get information about all routes registered by this plugin.

        Returns:
            List of route information including:
            - HTTP method
            - Path
            - Description
            - Parameters (query/path parameters)
            - Request body schema (for POST/PUT methods)
            - Response schema
        """
