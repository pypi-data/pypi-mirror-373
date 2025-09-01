from _typeshed import Incomplete
from bosa_server_plugins.auth.scheme import AuthenticationScheme as AuthenticationScheme
from bosa_server_plugins.cache import CacheService as CacheService
from bosa_server_plugins.github.constant import DEFAULT_ITEM_PER_PAGE as DEFAULT_ITEM_PER_PAGE
from bosa_server_plugins.github.gql.fragments.pull_request import GQLPullRequest as GQLPullRequest
from bosa_server_plugins.github.gql.pull_request import gql_get_pull_request as gql_get_pull_request, gql_list_pull_requests as gql_list_pull_requests
from bosa_server_plugins.github.helper.pull_requests import search_pull_requests as search_pull_requests
from bosa_server_plugins.github.helper.search import SearchType as SearchType, github_search as github_search
from bosa_server_plugins.github.http.cursor_meta import GithubApiCursorMeta as GithubApiCursorMeta
from bosa_server_plugins.github.requests.issue import GithubSearchIssuePrRequest as GithubSearchIssuePrRequest
from bosa_server_plugins.github.requests.pull_requests import GQLListPullRequestsRequest as GQLListPullRequestsRequest, GetPullRequestRequest as GetPullRequestRequest, SearchPullRequestsRequest as SearchPullRequestsRequest
from bosa_server_plugins.handler import ExposedDefaultHeaders as ExposedDefaultHeaders, Router as Router
from typing import Callable

class GithubPullRequestsRoutes:
    """Github PRs Routes."""
    cache: Incomplete
    def __init__(self, router: Router, get_auth_scheme: Callable[[ExposedDefaultHeaders], AuthenticationScheme], cache: CacheService) -> None:
        """Initialize the GithubPullRequestsRoutes.

        Args:
            router (Router): The router object.
            get_auth_scheme (Callable[[ExposedDefaultHeaders], AuthenticationScheme]): The function to get
                the authentication scheme.
            cache (CacheService): The cache service.
        """
