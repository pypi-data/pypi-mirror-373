from _typeshed import Incomplete
from bosa_core import ConfigService as ConfigService
from bosa_core.authentication.client.service import ClientAwareService as ClientAwareService
from bosa_core.authentication.token.service.verify_token_service import VerifyTokenService as VerifyTokenService
from bosa_server_plugins.common.plugin import ThirdPartyIntegrationPlugin as ThirdPartyIntegrationPlugin
from bosa_server_plugins.google_admin.router import GoogleAdminApiRoutes as GoogleAdminApiRoutes
from bosa_server_plugins.handler.header import ExposedDefaultHeaders as ExposedDefaultHeaders
from bosa_server_plugins.handler.router import Router as Router
from typing import Any

class GoogleAdminApiPlugin(ThirdPartyIntegrationPlugin):
    """Google Admin API Plugin."""
    name: str
    version: str
    description: str
    client_aware_service: ClientAwareService
    verify_token_service: VerifyTokenService
    config: ConfigService
    router: Router
    scope: Incomplete
    def __init__(self) -> None:
        """Initializes the plugin."""
    def initialize_authorization(self, callback_url: str, headers: ExposedDefaultHeaders):
        """Initializes the plugin authorization.

        Args:
            callback_url: The callback URL.
            headers: The headers.

        Returns:
            The authorization URL.
        """
    def initialize_custom_configuration(self, configuration: dict[str, Any], headers: ExposedDefaultHeaders):
        """Initializes the plugin with custom configuration.

        Args:
            configuration: The custom configuration dictionary.
            headers: The headers.
        """
    def success_authorize_callback(self, **kwargs) -> None:
        """Callback for successful authorization.

        Args:
            **kwargs: The keyword arguments.
        """
    def remove_integration(self, user_identifier: str, headers: ExposedDefaultHeaders):
        """Removes the integration.

        Args:
            user_identifier: The user identifier to remove.
            headers: The headers.
        """
    def user_has_integration(self, headers: ExposedDefaultHeaders):
        """Checks if the user has an integration.

        Args:
            headers: The headers.

        Returns:
            True if the user has an integration, False otherwise.
        """
    def select_integration(self, user_identifier: str, headers: ExposedDefaultHeaders):
        """Selects the integration.

        Args:
            user_identifier: The user identifier to select.
            headers: The headers.
        """
    def get_integration(self, user_identifier: str, headers: ExposedDefaultHeaders):
        """Get the integration.

        Args:
            user_identifier: The user identifier.
            headers: The headers.
        """
