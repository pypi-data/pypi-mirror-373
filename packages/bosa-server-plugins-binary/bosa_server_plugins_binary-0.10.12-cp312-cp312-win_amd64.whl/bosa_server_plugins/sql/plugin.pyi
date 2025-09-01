from bosa_core import ConfigService as ConfigService
from bosa_core.authentication.client.service import ClientAwareService as ClientAwareService
from bosa_core.authentication.plugin.service import ThirdPartyIntegrationService as ThirdPartyIntegrationService
from bosa_core.authentication.token.service import VerifyTokenService as VerifyTokenService
from bosa_server_plugins.cache import CacheService as CacheService
from bosa_server_plugins.common.exception import IntegrationDoesNotExistException as IntegrationDoesNotExistException, IntegrationExistsException as IntegrationExistsException
from bosa_server_plugins.common.helper.integration import IntegrationHelper as IntegrationHelper
from bosa_server_plugins.common.plugin import ThirdPartyIntegrationPlugin as ThirdPartyIntegrationPlugin
from bosa_server_plugins.handler import ExposedDefaultHeaders as ExposedDefaultHeaders, Router as Router
from bosa_server_plugins.sql.config import SqlConfig as SqlConfig
from bosa_server_plugins.sql.router import SqlApiRouter as SqlApiRouter
from bosa_server_plugins.sql.service.url import SqlUrlService as SqlUrlService
from typing import Any

class SqlApiPlugin(ThirdPartyIntegrationPlugin):
    """SQL API Plugin."""
    BEARER_TOKEN_PREFIX: str
    TOKEN_NOT_FOUND_MESSAGE: str
    name: str
    version: str
    description: str
    config: ConfigService
    cache: CacheService
    router: Router
    client_aware_service: ClientAwareService
    third_party_integration_service: ThirdPartyIntegrationService
    token_service: VerifyTokenService
    integration_helper: IntegrationHelper
    routes: SqlApiRouter
    def __init__(self) -> None:
        """Initializes the plugin."""
    def initialize_authorization(self, callback_url: str, headers: ExposedDefaultHeaders):
        """Initializes the plugin authorization.

        This method is not supported by this plugin. Use initialize_custom_configuration instead.

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

        Returns:
            The configuration result URL or status.
        """
    def success_authorize_callback(self, **kwargs) -> None:
        """Success authorize callback.

        This plugin does not support OAuth2 authorization. Use success_custom_configuration instead.

        Args:
            **kwargs: The keyword arguments.
        """
    def remove_integration(self, user_identifier: str, headers: ExposedDefaultHeaders):
        """Removes the integration.

        Because this plugin does not store any token that needs to be revoked,
        we can just delete the integration.

        Args:
            user_identifier: The user identifier to remove.
            headers: The headers.
        """
    def user_has_integration(self, headers: ExposedDefaultHeaders):
        """Checks if the user has an integration.

        Args:
            headers: The headers.
        """
    def select_integration(self, user_identifier: str, headers: ExposedDefaultHeaders):
        """Selects the integration.

        Args:
            user_identifier: The user identifier to select.
            headers: The headers.
        """
    def get_integration(self, user_identifier: str, headers: ExposedDefaultHeaders):
        """Gets the integration.

        Args:
            user_identifier: The user identifier to get.
            headers: The headers.
        """
