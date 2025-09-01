from bosa_core.authentication.client.service import ClientAwareService as ClientAwareService
from bosa_core.authentication.plugin.service import ThirdPartyIntegrationService as ThirdPartyIntegrationService
from bosa_core.authentication.token.service import VerifyTokenService as VerifyTokenService
from bosa_server_plugins.common.exception import IntegrationDoesNotExistException as IntegrationDoesNotExistException
from bosa_server_plugins.handler import ExposedDefaultHeaders as ExposedDefaultHeaders, Router as Router
from bosa_server_plugins.handler.auth import ApiKeyAuthenticationSchema as ApiKeyAuthenticationSchema
from bosa_server_plugins.sql.routes.query import SqlQueryRoutes as SqlQueryRoutes

class SqlApiRouter:
    """SQL API Router."""
    INTEGRATION_NAME: str
    router: Router
    client_aware_service: ClientAwareService
    third_party_integration_service: ThirdPartyIntegrationService
    token_service: VerifyTokenService
    def __init__(self, router: Router, client_aware_service: ClientAwareService, third_party_integration_service: ThirdPartyIntegrationService, token_service: VerifyTokenService) -> None:
        """Initializes the router.

        Args:
            router (Router): The router to be used.
            client_aware_service (ClientAwareService): The client aware service to be used.
            third_party_integration_service (ThirdPartyIntegrationService): The third party integration service to be
            used.
            token_service (VerifyTokenService): The token service to be used.
        """
