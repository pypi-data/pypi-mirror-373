from _typeshed import Incomplete
from bosa_core import ConfigService as ConfigService
from bosa_core.authentication.plugin.service import ThirdPartyIntegrationService as ThirdPartyIntegrationService
from bosa_server_plugins.catapa.auth.auth import CatapaCredentials as CatapaCredentials
from bosa_server_plugins.catapa.response.user import UserInfo as UserInfo
from bosa_server_plugins.catapa.services.user import CatapaUserInfoService as CatapaUserInfoService
from bosa_server_plugins.handler import ExposedDefaultHeaders as ExposedDefaultHeaders, Router as Router
from typing import Callable

class CatapaUserRoutes:
    """Catapa User Route."""
    config: Incomplete
    def __init__(self, router: Router, get_auth_scheme: Callable[[ExposedDefaultHeaders], CatapaCredentials], config: ConfigService, third_party_integration_service: ThirdPartyIntegrationService) -> None:
        """Initialize Catapa User Routes.

        Args:
            router: Router instance
            get_auth_scheme: Function to get the authentication scheme
            config: Configuration service
            third_party_integration_service: Third party integration service
        """
