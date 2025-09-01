from _typeshed import Incomplete
from bosa_core.authentication.client.service import ClientAwareService as ClientAwareService
from bosa_core.authentication.plugin.service import ThirdPartyIntegrationService as ThirdPartyIntegrationService
from bosa_core.authentication.token.service import VerifyTokenService as VerifyTokenService
from bosa_server_plugins.auth.bearer import BearerTokenAuthentication as BearerTokenAuthentication
from bosa_server_plugins.auth.scheme import AuthenticationScheme as AuthenticationScheme
from bosa_server_plugins.cache import CacheService as CacheService
from bosa_server_plugins.common.exception import IntegrationDoesNotExistException as IntegrationDoesNotExistException
from bosa_server_plugins.github.routes.admin import GithubAdminRoutes as GithubAdminRoutes
from bosa_server_plugins.github.routes.issues import GithubIssuesRoutes as GithubIssuesRoutes
from bosa_server_plugins.github.routes.metrics import GithubMetricsRoutes as GithubMetricsRoutes
from bosa_server_plugins.github.routes.projects import GithubProjectsRoutes as GithubProjectsRoutes
from bosa_server_plugins.github.routes.pull_requests import GithubPullRequestsRoutes as GithubPullRequestsRoutes
from bosa_server_plugins.github.routes.repositories import GithubRepositoriesRoutes as GithubRepositoriesRoutes
from bosa_server_plugins.handler.auth.api_key import ApiKeyAuthenticationSchema as ApiKeyAuthenticationSchema
from bosa_server_plugins.handler.header import ExposedDefaultHeaders as ExposedDefaultHeaders
from bosa_server_plugins.handler.router import Router as Router
from typing import Callable

class GithubApiRoutes:
    """Github API Routes."""
    INTEGRATION_NAME: str
    router: Router
    client_aware_service: Incomplete
    token_service: Incomplete
    cache: Incomplete
    def __init__(self, router: Router, get_default_auth_scheme: Callable[[], AuthenticationScheme], client_aware_service: ClientAwareService, token_service: VerifyTokenService, third_party_integration_service: ThirdPartyIntegrationService, cache: CacheService) -> None:
        """Initialize Github API Routes.

        Args:
            router: Router instance
            get_default_auth_scheme: Function to get the default authentication scheme
            client_aware_service: Client aware service
            token_service: Verify token service
            third_party_integration_service: Third party integration service
            cache: Cache service
        """
