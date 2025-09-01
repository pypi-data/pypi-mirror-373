from _typeshed import Incomplete
from bosa_server_plugins.auth.scheme import AuthenticationScheme as AuthenticationScheme
from bosa_server_plugins.cache import CacheService as CacheService
from bosa_server_plugins.github.helper.commits import search_repository_commits as search_repository_commits
from bosa_server_plugins.github.helper.contributions import ContributionStats as ContributionStats, search_contributors as search_contributors
from bosa_server_plugins.github.helper.metrics import get_repository_contributors as get_repository_contributors
from bosa_server_plugins.github.helper.repositories import get_repository_collaborators as get_repository_collaborators, get_repository_commits as get_repository_commits, get_repository_languages as get_repository_languages, get_repository_releases as get_repository_releases
from bosa_server_plugins.github.requests import BasicRepositoryRequest as BasicRepositoryRequest, GetCollaboratorsRequest as GetCollaboratorsRequest, GetCommitsRequest as GetCommitsRequest, GetReleasesRequest as GetReleasesRequest
from bosa_server_plugins.github.requests.commits import SearchCommitsRequest as SearchCommitsRequest
from bosa_server_plugins.github.requests.repositories import GetContributorsRequest as GetContributorsRequest, SearchContributorsRequest as SearchContributorsRequest
from bosa_server_plugins.handler import ExposedDefaultHeaders as ExposedDefaultHeaders, Router as Router
from bosa_server_plugins.handler.response import PaginationMeta as PaginationMeta
from typing import Callable

class SummaryMeta:
    """Summary metadata."""
    summary: dict
    page: PaginationMeta

class GithubRepositoriesRoutes:
    """Github Repo Routes."""
    cache: Incomplete
    def __init__(self, router: Router, get_auth_scheme: Callable[[ExposedDefaultHeaders], AuthenticationScheme], cache: CacheService) -> None:
        """Initialize the GithubRepositoriesRoutes.

        Args:
            router (Router): The router object.
            get_auth_scheme (Callable[[ExposedDefaultHeaders], AuthenticationScheme]): The function to get
                the authentication scheme.
            cache (CacheService): The cache service.
        """
