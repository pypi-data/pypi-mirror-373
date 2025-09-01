from _typeshed import Incomplete
from bosa_server_plugins.auth.scheme import AuthenticationScheme as AuthenticationScheme
from bosa_server_plugins.cache import CacheService as CacheService
from bosa_server_plugins.github.gql.issue import GQLIssue as GQLIssue, gql_get_issue as gql_get_issue, gql_list_issues as gql_list_issues
from bosa_server_plugins.github.helper.issues import create_issue as create_issue, get_issue_comments as get_issue_comments, search_issues as search_issues
from bosa_server_plugins.github.helper.search import SearchType as SearchType, github_search as github_search
from bosa_server_plugins.github.http.cursor_meta import GithubApiCursorMeta as GithubApiCursorMeta
from bosa_server_plugins.github.requests import CreateIssueRequest as CreateIssueRequest
from bosa_server_plugins.github.requests.issue import GQLListIssuesRequest as GQLListIssuesRequest, GetIssueCommentsRequest as GetIssueCommentsRequest, GetIssueRequest as GetIssueRequest, GithubSearchIssuePrRequest as GithubSearchIssuePrRequest, SearchIssuesRequest as SearchIssuesRequest
from bosa_server_plugins.handler import ExposedDefaultHeaders as ExposedDefaultHeaders, Router as Router
from typing import Callable

class GithubIssuesRoutes:
    """Github Issues Route."""
    cache: Incomplete
    def __init__(self, router: Router, get_auth_scheme: Callable[[ExposedDefaultHeaders], AuthenticationScheme], cache: CacheService) -> None:
        """Initialize the GithubIssuesRoutes.

        Args:
            router (Router): The router object.
            get_auth_scheme (Callable[[ExposedDefaultHeaders], AuthenticationScheme]):
                The function to get the authentication scheme.
            cache (CacheService): The cache service.
        """
