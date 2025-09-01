from .pagination import create_github_pagination_meta as create_github_pagination_meta
from _typeshed import Incomplete
from bosa_server_plugins.auth.scheme import AuthenticationScheme as AuthenticationScheme
from bosa_server_plugins.cache import CacheService as CacheService
from bosa_server_plugins.github.entities.issue import Issue as Issue
from bosa_server_plugins.github.gql.issue import gql_get_all_issues_project_details as gql_get_all_issues_project_details
from bosa_server_plugins.github.gql.project_details import GQLProjectDetails as GQLProjectDetails
from bosa_server_plugins.github.helper.common import convert_to_datetime as convert_to_datetime, count_items as count_items, get_repository_objects as get_repository_objects, resolve_repositories as resolve_repositories
from bosa_server_plugins.github.helper.connect import send_request_to_github as send_request_to_github
from bosa_server_plugins.github.helper.model.common import Direction as Direction
from enum import StrEnum
from typing import Any

GITHUB_ISSUE_COMMENT_CACHE_KEY: str
GITHUB_ISSUE_COMMENT_CACHE_TTL: int

class IssueState(StrEnum):
    """REST API issue state model."""
    OPEN = 'open'
    CLOSED = 'closed'
    ALL = 'all'

class IssueOrderBy(StrEnum):
    """REST API issue order by model."""
    CREATED = 'created'
    UPDATED = 'updated'
    COMMENTS = 'comments'

class IssueFields(StrEnum):
    """REST API issue fields model."""
    REPOSITORY = 'repository'
    NUMBER = 'number'
    TITLE = 'title'
    CREATOR = 'creator'
    BODY = 'body'
    STATE = 'state'
    URL = 'url'
    LABELS = 'labels'
    MILESTONE = 'milestone'
    COMMENTS = 'comments'
    ASSIGNEE = 'assignee'
    ASSIGNEES = 'assignees'
    CREATED_AT = 'created_at'
    UPDATED_AT = 'updated_at'
    PROJECT_DETAILS = 'project_details'

CORE_FIELDS: Incomplete

def get_issue(owner: str, repo: str, issue_number: int, auth_scheme: AuthenticationScheme) -> Issue:
    """Get an issue in a repository.

    Args:
        owner (str): The account owner of the repository
        repo (str): The name of the repository
        issue_number (int): The issue number
        auth_scheme (AuthenticationScheme): Authentication scheme to use

    Returns:
        Issue object containing issue information
    """
def get_issues(owner: str, repo: str, auth_scheme: AuthenticationScheme, *, milestone: str | None = None, state: IssueState | None = None, assignee: str | None = None, creator: str | None = None, mentioned: str | None = None, labels: str | None = None, sort: str | None = None, direction: str | None = None, since: str | None = None, per_page: int | None = 30, page: int | None = 1) -> tuple[list[Issue], dict]:
    """Get all issues in a repository.

    Args:
        owner: The account owner of the repository
        repo: The name of the repository
        auth_scheme: Authentication scheme to use
        milestone: Only issues with the specified milestone are returned
        state: Only issues with the specified state are returned
        assignee: Only issues assigned to the specified user are returned
        creator: Only issues created by the specified user are returned
        mentioned: Only issues mentioning the specified user are returned
        labels: Only issues with the specified labels are returned
        sort: How to sort the issues. Options are: created, updated, popularity, long-running
        direction: The sort direction. Options are: asc, desc
        since: Only issues updated at or after this time are returned
        per_page: Number of issues to return per page
        page: Page number

    Returns:
        List of Issue objects containing issue information
    """
def get_issue_comments(owner: str, repo: str, issue_number: int, auth_scheme: AuthenticationScheme, *, force_new: bool = False, created_at_from: str | None = None, created_at_to: str | None = None, updated_at_from: str | None = None, updated_at_to: str | None = None, per_page: int | None = None, page: int | None = None, cache_service: CacheService) -> tuple[list[Any], dict]:
    """Get all comments on an issue in a repository.

    Args:
        owner: The account owner of the repository
        repo: The name of the repository
        issue_number: The issue number
        auth_scheme: Authentication scheme to use
        force_new: Whether to force a new request to the API
        created_at_from: Only comments created at or after this time are returned
        created_at_to: Only comments created at or before this time are returned
        updated_at_from: Only comments updated at or after this time are returned
        updated_at_to: Only comments updated at or before this time are returned
        per_page: Number of comments to return per page
        page: Page number,
        cache_service: The cache service to use

    Returns:
        List of Issue Comments
    """
def create_issue(owner: str, repo: str, auth_scheme: AuthenticationScheme, title: str, body: str | None = None, assignees: list[str] | None = None, labels: list[str] | None = None, milestone: int | None = None) -> Issue:
    """Create a new issue in a repository.

    Args:
        owner: The account owner of the repository
        repo: The name of the repository
        auth_scheme: Authentication scheme to use
        title: The title of the issue
        body: The body of the issue
        assignees: The assignees of the issue
        labels: The labels of the issue
        milestone: The milestone of the issue

    Returns:
        Issue object containing the created issue information
    """
def search_issues(auth_scheme: AuthenticationScheme, *, repositories: list[str] | None = None, since: str | None = None, until: str | None = None, state: IssueState | None = None, creator: str | None = None, fields: list[IssueFields] | None = None, summarize: bool | None = False, sort: IssueOrderBy | None = None, direction: Direction | None = None, labels: list[str] | None = None, assignee: str | None = None, milestone: int | None = None) -> Any:
    """Search for issues in repositories.

    Args:
        auth_scheme: Authentication scheme to use
        repositories: List of repositories to search in
        since: Only issues updated at or after this time are returned
        until: Only issues updated at or before this time are returned
        state: Only issues with the specified state are returned
        creator: Only issues created by the specified user are returned
        fields: List of fields to include in the response
        summarize: Control the level of detail in the results
        sort: Sort issues by creation or update time
        direction: Sort direction (asc or desc)
        labels: Only issues with the specified labels are returned
        assignee: Only issues assigned to the specified user are returned
        milestone: Only issues with the specified milestone are returned

    Returns:
        Dictionary containing search results
    """
