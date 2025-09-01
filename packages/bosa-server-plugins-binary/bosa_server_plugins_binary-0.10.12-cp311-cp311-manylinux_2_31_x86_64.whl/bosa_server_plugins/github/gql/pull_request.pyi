from _typeshed import Incomplete
from bosa_server_plugins.auth.scheme import AuthenticationScheme as AuthenticationScheme
from bosa_server_plugins.github.gql.common import GQLDirection as GQLDirection, GQLIssueOrderBy as GQLIssueOrderBy, construct_page_query as construct_page_query
from bosa_server_plugins.github.gql.fragments.issue_simple import ISSUE_SIMPLE_FRAGMENT as ISSUE_SIMPLE_FRAGMENT
from bosa_server_plugins.github.gql.fragments.label import LABEL_FRAGMENT as LABEL_FRAGMENT
from bosa_server_plugins.github.gql.fragments.pull_request import GQLPullRequest as GQLPullRequest, PULL_REQUEST_FRAGMENT as PULL_REQUEST_FRAGMENT
from bosa_server_plugins.github.gql.fragments.pull_request_project_details import GQLPullRequestProjectDetails as GQLPullRequestProjectDetails, PULL_REQUEST_PROJECT_DETAILS_FRAGMENT as PULL_REQUEST_PROJECT_DETAILS_FRAGMENT
from bosa_server_plugins.github.gql.fragments.repository import REPOSITORY_FRAGMENT as REPOSITORY_FRAGMENT
from bosa_server_plugins.github.gql.project import CONTENTLESS_PROJECT_ITEM_FRAGMENT as CONTENTLESS_PROJECT_ITEM_FRAGMENT, PROJECT_FRAGMENT as PROJECT_FRAGMENT
from bosa_server_plugins.github.helper.connect import query_github_gql as query_github_gql
from bosa_server_plugins.github.http.cursor_meta import GithubApiCursorMeta as GithubApiCursorMeta
from enum import Enum

class GQLPullRequestState(str, Enum):
    """Pull request state model."""
    OPEN = 'OPEN'
    CLOSED = 'CLOSED'
    MERGED = 'MERGED'

GQL_GET_PULL_REQUEST_QUERY: Incomplete
GQL_GET_REPOSITORY_PULL_REQUEST_PROJECT_DETAILS_QUERY: Incomplete
GQL_LIST_PULL_REQUESTS_QUERY: Incomplete

def gql_get_pull_request(auth_scheme: AuthenticationScheme, *, owner: str, repo: str, pull_request_id: int) -> GQLPullRequest:
    """Get a pull request by ID.

    Args:
        auth_scheme: Authentication scheme to use
        owner: The account owner of the repository
        repo: The name of the repository
        pull_request_id: The ID of the pull request

    Returns:
        GQLPullRequest: The created pull request complete.
    """
def gql_list_pull_requests(auth_scheme: AuthenticationScheme, *, owner: str, repo: str, states: list[GQLPullRequestState] | None = None, labels: list[str] | None = None, head: str | None = None, base: str | None = None, per_page: int = 100, cursor: str | None = None, from_last: bool = False, order_by: GQLIssueOrderBy = ..., direction: GQLDirection = ...) -> tuple[list[GQLPullRequest], GithubApiCursorMeta]:
    """Get a list of pull requests in a repository.

    Args:
        auth_scheme: Authentication scheme to use
        owner: The account owner of the repository
        repo: The name of the repository
        states: List of states to filter by (OPEN, CLOSED, MERGED)
        labels: List of labels to filter by
        head: The head ref name to filter by
        base: The base ref name to filter by
        per_page: Number of pull requests per page
        cursor: Cursor for pagination
        from_last: Whether to paginate from the end
        order_by: Field to order by
        direction: Direction to order by

    Returns:
        tuple[list[GQLPullRequest], GithubApiCursorMeta]: A tuple containing the list of pull requests
        and pagination metadata
    """
def gql_get_all_pull_request_project_details(auth_scheme: AuthenticationScheme, *, owner: str, repo: str) -> list[GQLPullRequestProjectDetails]:
    """Get the project details for all pull requests in a repository.

    Args:
        auth_scheme: Authentication scheme to use
        owner: The account owner of the repository
        repo: The name of the repository

    Returns:
        List[GQLPullRequestProjectDetails]: List of PR project details
    """
