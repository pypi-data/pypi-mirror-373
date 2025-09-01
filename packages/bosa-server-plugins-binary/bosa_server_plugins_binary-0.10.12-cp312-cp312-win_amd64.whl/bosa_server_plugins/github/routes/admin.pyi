from _typeshed import Incomplete
from bosa_core.authentication.plugin.service import ThirdPartyIntegrationService as ThirdPartyIntegrationService
from bosa_server_plugins.github.constant import STATUS_CODE_NOT_FOUND as STATUS_CODE_NOT_FOUND
from bosa_server_plugins.github.helper.revoke import revoke_github_access_token as revoke_github_access_token
from bosa_server_plugins.handler import ExposedDefaultHeaders as ExposedDefaultHeaders, Router as Router
from bosa_server_plugins.handler.auth.api_key import ApiKeyAuthenticationSchema as ApiKeyAuthenticationSchema
from bosa_server_plugins.handler.response import ApiResponse as ApiResponse

logger: Incomplete

class GithubAdminRoutes:
    """Github Admin Route."""
    third_party_integration_service: Incomplete
    def __init__(self, router: Router, third_party_integration_service: ThirdPartyIntegrationService) -> None:
        """Initialize the GithubAdminRoutes.

        Args:
            router (Router): The router object.
            third_party_integration_service (ThirdPartyIntegrationService):
                The third party integration service.
        """
