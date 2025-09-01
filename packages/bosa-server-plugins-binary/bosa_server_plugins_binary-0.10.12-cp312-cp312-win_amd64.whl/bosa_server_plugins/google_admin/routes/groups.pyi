from bosa_server_plugins.google.auth.auth import GoogleCredentials as GoogleCredentials
from bosa_server_plugins.google.response.pagination import PaginationMeta as PaginationMeta
from bosa_server_plugins.google_admin.requests.groups import ListGroupsRequest as ListGroupsRequest
from bosa_server_plugins.google_admin.response.groups import Group as Group
from bosa_server_plugins.google_admin.services.groups import GoogleAdminGroupsService as GoogleAdminGroupsService
from bosa_server_plugins.handler import ExposedDefaultHeaders as ExposedDefaultHeaders, Router as Router
from typing import Callable

class GoogleAdminGroupsRoutes:
    """Google Admin Groups Route."""
    def __init__(self, router: Router, get_auth_scheme: Callable[[ExposedDefaultHeaders], GoogleCredentials]) -> None:
        """Initialize the Google Admin Groups Route.

        Args:
            router: The router to register the routes with.
            get_auth_scheme: A function to get the authentication scheme.
        """
