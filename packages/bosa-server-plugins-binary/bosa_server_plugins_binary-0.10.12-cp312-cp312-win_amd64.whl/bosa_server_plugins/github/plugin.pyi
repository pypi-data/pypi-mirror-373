from _typeshed import Incomplete
from bosa_core import ConfigService as ConfigService
from bosa_core.authentication.client.service import ClientAwareService as ClientAwareService
from bosa_core.authentication.plugin.service import ThirdPartyIntegrationService as ThirdPartyIntegrationService
from bosa_core.authentication.token.service import VerifyTokenService as VerifyTokenService
from bosa_server_plugins.auth.bearer import BearerTokenAuthentication as BearerTokenAuthentication
from bosa_server_plugins.auth.scheme import AuthenticationScheme as AuthenticationScheme
from bosa_server_plugins.cache import CacheService as CacheService
from bosa_server_plugins.common.exception import IntegrationDoesNotExistException as IntegrationDoesNotExistException
from bosa_server_plugins.common.helper.integration import IntegrationHelper as IntegrationHelper
from bosa_server_plugins.common.plugin import ThirdPartyIntegrationPlugin as ThirdPartyIntegrationPlugin
from bosa_server_plugins.github.constant import STATUS_CODE_NOT_FOUND as STATUS_CODE_NOT_FOUND
from bosa_server_plugins.github.helper.revoke import revoke_github_access_token as revoke_github_access_token
from bosa_server_plugins.github.router import GithubApiRoutes as GithubApiRoutes
from bosa_server_plugins.handler.header import ExposedDefaultHeaders as ExposedDefaultHeaders
from bosa_server_plugins.handler.router import Router as Router
from typing import Any

TOKEN_NOT_FOUND_MESSAGE: str

class GithubApiPlugin(ThirdPartyIntegrationPlugin):
    """Github API Plugin."""
    CURRENT_API_VERSION: str
    BASE_GITHUB_URL: str
    BASE_API_GITHUB_URL: str
    BEARER_TOKEN_PREFIX: str
    GITHUB_STATE_CACHE_TTL: int
    DEFAULT_TIMEOUT: int
    name: str
    version: str
    description: str
    config: ConfigService
    cache: CacheService
    router: Router
    client_aware_service: ClientAwareService
    token_service: VerifyTokenService
    third_party_integration_service: ThirdPartyIntegrationService
    integration_helper: IntegrationHelper
    routes: GithubApiRoutes
    auth_scheme: AuthenticationScheme
    auth_scopes: Incomplete
    api_key: Incomplete
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
    def user_has_integration(self, headers: ExposedDefaultHeaders):
        """Checks if the current active user has integration with Github.

        Args:
            headers (ExposedDefaultHeaders): The headers to use.

        Returns:
            bool: True if the user has integration with Github, False otherwise.
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
    def with_authentication_scheme(self, scheme: AuthenticationScheme):
        """Sets the authentication scheme for the plugin.

        Args:
            scheme (AuthenticationScheme): The authentication scheme to use.
        """
