from _typeshed import Incomplete
from bosa_core import ConfigService as ConfigService
from bosa_core.authentication.client.service import ClientAwareService as ClientAwareService
from bosa_core.authentication.token.service.verify_token_service import VerifyTokenService as VerifyTokenService
from bosa_server_plugins.google.auth.auth import GoogleCredentials as GoogleCredentials
from bosa_server_plugins.google.auth.service_account import ServiceAccountGoogleCredentials as ServiceAccountGoogleCredentials
from bosa_server_plugins.google_admin.routes.groups import GoogleAdminGroupsRoutes as GoogleAdminGroupsRoutes
from bosa_server_plugins.handler.auth.api_key import ApiKeyAuthenticationSchema as ApiKeyAuthenticationSchema
from bosa_server_plugins.handler.header import ExposedDefaultHeaders as ExposedDefaultHeaders
from bosa_server_plugins.handler.router import Router as Router

class GoogleAdminApiRoutes:
    """Google Admin API Routes."""
    config: Incomplete
    client_aware_service: Incomplete
    verify_token_service: Incomplete
    scopes: Incomplete
    def __init__(self, scopes: list[str], router: Router, config: ConfigService, client_aware_service: ClientAwareService, verify_token_service: VerifyTokenService) -> None:
        """Initialize the Google Admin API Routes.

        Args:
            router: The router to register the routes with.
            config: The config service.
            client_aware_service: The client aware service.
            verify_token_service: The verify token service.
            scopes: The scopes.
        """
