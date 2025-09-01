from bosa_server_plugins.auth.scheme import AuthenticationScheme as AuthenticationScheme
from bosa_server_plugins.cache import CacheService as CacheService
from bosa_server_plugins.github.entities.project import Project as Project, ProjectItem as ProjectItem, ProjectListMeta as ProjectListMeta
from bosa_server_plugins.github.helper.projects import ProjectSummary as ProjectSummary, get_items_from_project as get_items_from_project, get_projects_list as get_projects_list
from bosa_server_plugins.github.requests.projects import GithubListProjectCardsRequest as GithubListProjectCardsRequest, GithubListProjectsRequest as GithubListProjectsRequest
from bosa_server_plugins.handler import ExposedDefaultHeaders as ExposedDefaultHeaders, Router as Router
from typing import Callable

class GithubProjectsRoutes:
    """Github Project Routes."""
    def __init__(self, router: Router, get_auth_scheme: Callable[[ExposedDefaultHeaders], AuthenticationScheme], cache: CacheService) -> None:
        """Initialize the GithubProjectsRoutes.

        Args:
            router (Router): The router object.
            get_auth_scheme (Callable[[ExposedDefaultHeaders], AuthenticationScheme]): The function to get
                the authentication scheme.
            cache (CacheService): The cache service.
        """
