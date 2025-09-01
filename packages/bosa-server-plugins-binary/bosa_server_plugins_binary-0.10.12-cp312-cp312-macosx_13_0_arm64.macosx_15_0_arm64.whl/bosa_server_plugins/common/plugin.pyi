import abc
from abc import abstractmethod
from bosa_core import Plugin
from bosa_server_plugins.common.requests import AuthorizationRequest as AuthorizationRequest
from bosa_server_plugins.handler.decorators import public as public
from bosa_server_plugins.handler.header import ExposedDefaultHeaders as ExposedDefaultHeaders
from bosa_server_plugins.handler.interface import HttpHandler as HttpHandler
from bosa_server_plugins.handler.router import Router as Router
from starlette.requests import Request as Request
from typing import Any

INTEGRATIONS_WITH_USER_PATH: str

class ThirdPartyIntegrationPlugin(Plugin, metaclass=abc.ABCMeta):
    """Third Party Integration Plugin base class."""
    router: Router
    @property
    def authorize_callback_url(self) -> str:
        """The authorize callback URL.

        Returns:
            str: The authorize callback URL
        """
    def __init__(self) -> None:
        """Initialize the plugin."""
    @abstractmethod
    def initialize_authorization(self, callback_url: str, headers: ExposedDefaultHeaders):
        """Initializes the plugin authorization.

        Args:
            callback_url: The callback URL.
            headers: The headers.

        Returns:
            The authorization URL.
        """
    @abstractmethod
    def initialize_custom_configuration(self, configuration: dict[str, Any], headers: ExposedDefaultHeaders):
        """Initializes the plugin with custom configuration.

        Args:
            configuration: The custom configuration dictionary.
            headers: The headers.

        Returns:
            The configuration result URL or status.
        """
    @abstractmethod
    def success_authorize_callback(self, **kwargs):
        """Callback for successful authorization.

        Args:
            **kwargs: The keyword arguments.
        """
    @abstractmethod
    def remove_integration(self, user_identifier: str, headers: ExposedDefaultHeaders):
        """Removes the integration.

        Args:
            user_identifier: The user identifier to remove.
            headers: The headers.
        """
    @abstractmethod
    def user_has_integration(self, headers: ExposedDefaultHeaders):
        """Checks if the user has an integration.

        Args:
            headers: The headers.

        Returns:
            True if the user has an integration, False otherwise.
        """
    @abstractmethod
    def select_integration(self, user_identifier: str, headers: ExposedDefaultHeaders):
        """Selects the integration.

        Args:
            user_identifier: The user identifier to select.
            headers: The headers.
        """
    @abstractmethod
    def get_integration(self, user_identifier: str, headers: ExposedDefaultHeaders):
        """Get the integration.

        Args:
            user_identifier: The user identifier to select.
            headers: The headers.
        """
