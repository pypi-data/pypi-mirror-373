from _typeshed import Incomplete
from bosa_server_plugins.auth.scheme import AuthenticationScheme as AuthenticationScheme
from bosa_server_plugins.github.gql.common import GQLDirection as GQLDirection, GQLIssueOrderBy as GQLIssueOrderBy, construct_page_query as construct_page_query
from bosa_server_plugins.github.gql.fragments.issue import GQLIssue as GQLIssue, ISSUE_FRAGMENT as ISSUE_FRAGMENT
from bosa_server_plugins.github.gql.fragments.issue_project_details import GQLIssueProjectDetails as GQLIssueProjectDetails, ISSUE_PROJECT_DETAILS_FRAGMENT as ISSUE_PROJECT_DETAILS_FRAGMENT
from bosa_server_plugins.github.gql.fragments.label import LABEL_FRAGMENT as LABEL_FRAGMENT
from bosa_server_plugins.github.gql.fragments.milestone import MILESTONE_FRAGMENT as MILESTONE_FRAGMENT
from bosa_server_plugins.github.gql.fragments.pull_request_simple import PULL_REQUEST_SIMPLE_FRAGMENT as PULL_REQUEST_SIMPLE_FRAGMENT
from bosa_server_plugins.github.gql.fragments.repository import REPOSITORY_FRAGMENT as REPOSITORY_FRAGMENT
from bosa_server_plugins.github.gql.project import CONTENTLESS_PROJECT_ITEM_FRAGMENT as CONTENTLESS_PROJECT_ITEM_FRAGMENT, PROJECT_FRAGMENT as PROJECT_FRAGMENT
from bosa_server_plugins.github.helper.connect import query_github_gql as query_github_gql
from bosa_server_plugins.github.http.cursor_meta import GithubApiCursorMeta as GithubApiCursorMeta
from enum import StrEnum
from pydantic import BaseModel

class GQLIssueState(StrEnum):
    """Issue state enum."""
    OPEN = 'OPEN'
    CLOSED = 'CLOSED'

class GQLIssueFilter(BaseModel):
    """Issue filter model."""
    assignee: str | None
    created_by: str | None
    mentioned: str | None
    labels: list[str] | None
    milestone: str | None
    milestone_number: str | None
    since: str | None
    states: list[GQLIssueState] | None
    def to_dict(self) -> dict:
        """Convert the issue filter to a dictionary.

        Returns:
            dict: The dictionary representation of the issue filter.
        """

class GQLIssueOrder(BaseModel):
    """Issue order model."""
    field: GQLIssueOrderBy
    direction: str

GQL_GET_ISSUE_QUERY: Incomplete
GQL_GET_LIST_ISSUE_QUERY: Incomplete
GQL_GET_REPOSITORY_ISSUE_PROJECT_DETAILS_QUERY: Incomplete
GQL_GET_ISSUE_PROJECT_DETAILS_QUERY: Incomplete

def gql_get_issue(auth_scheme: AuthenticationScheme, *, owner: str, repo: str, issue_id: int) -> GQLIssue:
    """Get an issue by ID.

    Args:
        auth_scheme: Authentication scheme to use
        owner: The account owner of the repository
        repo: The name of the repository
        issue_id: The ID of the issue

    Returns:
        GQLIssue: The created issue.
    """
def gql_list_issues(auth_scheme: AuthenticationScheme, *, owner: str, repo: str, order_by: GQLIssueOrderBy = ..., direction: GQLDirection = ..., per_page: int = 100, cursor: str | None = None, from_last: bool = False, filter_by: GQLIssueFilter | None = None) -> tuple[list[GQLIssue], GithubApiCursorMeta]:
    """Get a list of issues in a repository.

    Args:
        auth_scheme: Authentication scheme to use
        owner: The account owner of the repository
        repo: The name of the repository
        order_by: The order by field
        direction: The direction of the order
        per_page: The number of issues per page
        cursor: The cursor to start from
        from_last: Whether to start from the last page
        filter_by: The filter to apply to the issues

    Returns:
        tuple[list[GQLIssue], int]: A tuple containing the list of issues and the total count
    """
def gql_get_all_issues_project_details(auth_scheme: AuthenticationScheme, *, owner: str, repo: str) -> list[GQLIssueProjectDetails]:
    """Get the project details for all issues in a repository.

    Args:
        auth_scheme: Authentication scheme to use
        owner: The account owner of the repository
        repo: The name of the repository

    Returns:
        List[GQLIssueProjectDetails]: List of issue project details
    """
