from bosa_core import ConfigService as ConfigService
from bosa_core.authentication.client.service import ClientAwareService as ClientAwareService
from bosa_core.authentication.plugin.service import ThirdPartyIntegrationService as ThirdPartyIntegrationService
from bosa_core.authentication.token.service.verify_token_service import VerifyTokenService as VerifyTokenService
from bosa_server_plugins.auth.scheme import AuthenticationScheme as AuthenticationScheme
from bosa_server_plugins.cache import CacheService as CacheService
from bosa_server_plugins.catapa.auth.auth import CatapaCredentials as CatapaCredentials
from bosa_server_plugins.catapa.router import CatapaApiRoutes as CatapaApiRoutes
from bosa_server_plugins.catapa.services.base import CatapaServiceBase as CatapaServiceBase
from bosa_server_plugins.common.exception import IntegrationDoesNotExistException as IntegrationDoesNotExistException
from bosa_server_plugins.common.helper.integration import IntegrationHelper as IntegrationHelper
from bosa_server_plugins.common.plugin import ThirdPartyIntegrationPlugin as ThirdPartyIntegrationPlugin
from bosa_server_plugins.handler import ExposedDefaultHeaders as ExposedDefaultHeaders, Router as Router
from typing import Any

TOKEN_NOT_FOUND_MESSAGE: str

class CatapaPlugin(ThirdPartyIntegrationPlugin):
    """Catapa API Plugin."""
    BEARER_TOKEN_PREFIX: str
    DEFAULT_TIMEOUT: int
    name: str
    version: str
    description: str
    config: ConfigService
    cache: CacheService
    router: Router
    client_aware_service: ClientAwareService
    verify_token_service: VerifyTokenService
    third_party_integration_service: ThirdPartyIntegrationService
    integration_helper: IntegrationHelper
    auth_scheme: AuthenticationScheme
    def __init__(self) -> None:
        """Initializes the plugin."""
    @property
    def authorization_url(self) -> str:
        """Get the authorization URL from config."""
    @property
    def base_url(self) -> str:
        """Get the base URL from config."""
    @property
    def api_version(self) -> str:
        """Get the default API version from config."""
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

        Returns:
            The configuration result URL or status.
        """
    def success_authorize_callback(self, **kwargs):
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
    def select_integration(self, user_identifier: str, headers: ExposedDefaultHeaders):
        """Selects the integration.

        Args:
            user_identifier: The user identifier to select.
            headers: The headers.
        """
    def user_has_integration(self, headers: ExposedDefaultHeaders):
        """Checks if the current active user has integration with Catapa.

        Args:
            headers (ExposedDefaultHeaders): The headers to use.

        Returns:
            bool: True if the user has integration with Catapa, False otherwise.
        """
    def get_integration(self, user_identifier: str, headers: ExposedDefaultHeaders):
        """Get the integration with fresh tokens.

        Args:
            user_identifier: The user identifier.
            headers: The headers.

        Returns:
            The integration with refreshed tokens.
        """
    def with_authentication_scheme(self, scheme: AuthenticationScheme):
        """Sets the authentication scheme for the plugin.

        Args:
            scheme (AuthenticationScheme): The authentication scheme to use.
        """
