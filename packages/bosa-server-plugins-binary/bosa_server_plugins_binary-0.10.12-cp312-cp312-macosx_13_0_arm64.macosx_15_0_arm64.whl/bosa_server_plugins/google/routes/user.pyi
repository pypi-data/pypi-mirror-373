from _typeshed import Incomplete
from bosa_server_plugins.cache import CacheService as CacheService
from bosa_server_plugins.google.auth.auth import GoogleCredentials as GoogleCredentials
from bosa_server_plugins.google.services.user_info import GoogleUserInfoService as GoogleUserInfoService
from bosa_server_plugins.handler import ExposedDefaultHeaders as ExposedDefaultHeaders, Router as Router
from typing import Callable

class GoogleUserRoutes:
    """Google User Route."""
    cache: Incomplete
    def __init__(self, router: Router, get_auth_scheme: Callable[[ExposedDefaultHeaders], GoogleCredentials], cache: CacheService) -> None:
        """Initialize Google User Routes.

        Args:
            router: Router instance
            get_auth_scheme: Function to get the authentication scheme
            cache: Cache service
        """
