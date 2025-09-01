from _typeshed import Incomplete
from bosa_core import ConfigService as ConfigService
from bosa_core.authentication.client.service import ClientAwareService as ClientAwareService
from bosa_core.authentication.plugin.service import ThirdPartyIntegrationService as ThirdPartyIntegrationService
from bosa_core.authentication.token.service.verify_token_service import VerifyTokenService as VerifyTokenService
from bosa_server_plugins.auth.scheme import AuthenticationScheme as AuthenticationScheme
from bosa_server_plugins.cache import CacheService as CacheService
from bosa_server_plugins.common.exception import IntegrationDoesNotExistException as IntegrationDoesNotExistException
from bosa_server_plugins.google.auth.auth import GoogleCredentials as GoogleCredentials
from bosa_server_plugins.google.routes.user import GoogleUserRoutes as GoogleUserRoutes
from bosa_server_plugins.handler import ExposedDefaultHeaders as ExposedDefaultHeaders, Router as Router
from bosa_server_plugins.handler.auth import ApiKeyAuthenticationSchema as ApiKeyAuthenticationSchema
from typing import Callable

class GoogleApiRoutes:
    """Google API Routes."""
    INTEGRATION_NAME: str
    router: Router
    client_aware_service: Incomplete
    verify_token_service: Incomplete
    cache: Incomplete
    config: Incomplete
    def __init__(self, router: Router, get_default_auth_scheme: Callable[[], AuthenticationScheme], client_aware_service: ClientAwareService, verify_token_service: VerifyTokenService, third_party_integration_service: ThirdPartyIntegrationService, cache: CacheService, config: ConfigService) -> None:
        """Initialize Google API Routes.

        Args:
            router: Router instance
            get_default_auth_scheme: Function to get the default authentication scheme
            client_aware_service: Client aware service
            verify_token_service: Verify token service
            third_party_integration_service: ThirdPartyIntegrationService
            cache: Cache service
            config: Config service
        """
