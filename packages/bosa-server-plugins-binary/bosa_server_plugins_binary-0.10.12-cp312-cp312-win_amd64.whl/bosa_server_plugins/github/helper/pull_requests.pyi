from .pagination import create_github_pagination_meta as create_github_pagination_meta
from bosa_server_plugins.auth.scheme import AuthenticationScheme as AuthenticationScheme
from bosa_server_plugins.github.gql.project_details import GQLProjectDetails as GQLProjectDetails
from bosa_server_plugins.github.gql.pull_request import gql_get_all_pull_request_project_details as gql_get_all_pull_request_project_details
from bosa_server_plugins.github.helper.common import count_items as count_items, get_repository_objects as get_repository_objects, resolve_repositories as resolve_repositories
from bosa_server_plugins.github.helper.connect import send_request_to_github as send_request_to_github
from bosa_server_plugins.github.helper.model.common import Direction as Direction
from enum import StrEnum
from github.PullRequest import PullRequest as PullRequest
from typing import Any

DATE_FORMAT: str

class PrState(StrEnum):
    """Pull request state model."""
    OPEN = 'open'
    CLOSED = 'closed'
    ALL = 'all'

class PrOrderBy(StrEnum):
    """Pull request order by model."""
    CREATED = 'created'
    UPDATED = 'updated'
    POPULARITY = 'popularity'
    LONG_RUNNING = 'long-running'

class PullRequestFields(StrEnum):
    """Pull request fields model."""
    REPOSITORY = 'repository'
    NUMBER = 'number'
    TITLE = 'title'
    AUTHOR = 'author'
    BODY = 'body'
    STATE = 'state'
    DRAFT = 'draft'
    URL = 'url'
    LABELS = 'labels'
    MILESTONE = 'milestone'
    ASSIGNEE = 'assignee'
    ASSIGNEES = 'assignees'
    CREATED_AT = 'created_at'
    MERGED_AT = 'merged_at'
    UPDATED_AT = 'updated_at'
    PROJECT_DETAILS = 'project_details'

def validate_merged_status(raw_data, filters):
    """Validate the merged status of a pull request based on filters.

    Args:
        raw_data: The raw data of the pull request.
        filters: A dictionary of filters to apply.

    Returns:
        bool: True if the PR matches the merged filter, False otherwise.
    """
def validate_draft_status(raw_data, filters):
    """Validate the draft status of a pull request based on filters.

    Args:
        raw_data: The raw data of the pull request.
        filters: A dictionary of filters to apply.

    Returns:
        bool: True if the PR matches the draft filter, False otherwise.
    """
def validate_author(raw_data, filters):
    """Validate the author of a pull request based on filters.

    Args:
        raw_data: The raw data of the pull request.
        filters: A dictionary of filters to apply.

    Returns:
        bool: True if the PR matches the author filter, False otherwise.
    """
def validate_labels(raw_data, filters):
    """Validate the labels of a pull request based on filters.

    Args:
        raw_data: The raw data of the pull request.
        filters: A dictionary of filters to apply.

    Returns:
        bool: True if the PR matches the labels filter, False otherwise.
    """
def validate_date(raw_data: dict[str, Any], filters: dict[str, Any]) -> bool:
    """Validate if a PR matches the date filters.

    Args:
        raw_data: The raw data of the pull request.
        filters: A dictionary of filters to apply.

    Returns:
        bool: True if the PR matches the date filters, False otherwise.
    """
def get_pull_requests(owner: str, repo: str, auth_scheme: AuthenticationScheme, *, state: str | None = None, head: str | None = None, base: str | None = None, sort: str | None = None, direction: str | None = None, per_page: int | None = None, page: int | None = None) -> tuple[list[Any], Any]:
    """Lists the pull requests of a repository.

    Args:
        owner: The owner of the repository.
        repo: The repository name.
        auth_scheme: The authentication scheme.
        state: The state of the pull requests. Can be either 'open', 'closed' or 'all'.
        head: The head branch.
        base: The base branch.
        sort: The sort order. Can be 'created', 'updated', 'popularity' or 'long-running'.
        direction: The sort direction. Can be 'asc' or 'desc'.
        per_page: The number of pull requests to return per page.
        page: The page number.

    Returns:
        tuple[List[Any], Any]: A tuple containing:
        - List[PullRequest]: The list of pull requests.
        - Any: The pagination metadata.
    """
def search_pull_requests(auth_scheme: AuthenticationScheme, *, repositories: list[str] | None = None, merged: bool | None = None, draft: bool | None = None, author: str | None = None, labels: list[str] | None = None, since: str | None = None, until: str | None = None, state: PrState | None = None, sort: PrOrderBy | None = None, direction: Direction | None = None, fields: list[PullRequestFields] | None = None, summarize: bool | None = False) -> Any:
    """Search for pull requests in a repository.

    Args:
        auth_scheme: The authentication scheme
        repositories: List of repositories to search
        merged: Whether to filter for merged pull requests
        draft: Whether to filter for draft pull requests
        author: GitHub login of the PR author
        labels: List of labels to filter by
        since: Start date for created date filter
        until: End date for created date filter
        state: The state of the pull requests. Can be either 'open', 'closed' or 'all'.
        sort: The sort order. Can be 'created', 'updated', 'popularity' or 'long-running'.
        direction: The sort direction. Can be 'asc' or 'desc'.
        fields: Optional list of fields to include in the output
        summarize: Whether to include summary information

    Returns:
        Tuple containing list of pull requests, total count, and optional summary
    """
def get_pull_request(owner: str, repo: str, pull_number: int, auth_scheme: AuthenticationScheme):
    """Get on pull request data of a repository.

    Args:
        owner: The owner of the repository.
        repo: The repository name.
        pull_number: The pull request number.
        auth_scheme: The authentication scheme.

    Returns:
        PullRequest: The pull request data.
    """
