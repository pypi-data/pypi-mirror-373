from _typeshed import Incomplete
from bosa_server_plugins.common.cache import serialize_cache_data as serialize_cache_data
from bosa_server_plugins.common.callback import delete_callback_urls as delete_callback_urls, get_callback_urls as get_callback_urls, with_callbacks as with_callbacks
from bosa_server_plugins.github.constant import AUTH_CACHE_KEY_FORMAT as AUTH_CACHE_KEY_FORMAT, GITHUB_DATE_FORMAT as GITHUB_DATE_FORMAT, GITHUB_PR_COMMITS_CACHE_TTL as GITHUB_PR_COMMITS_CACHE_TTL
from bosa_server_plugins.github.entities.commit import CommitSearchContext as CommitSearchContext, SearchFilters as SearchFilters
from bosa_server_plugins.github.utils.commit import generate_search_commit_key as generate_search_commit_key, get_all_cached_data as get_all_cached_data, get_cached_data as get_cached_data, get_wrapped_result as get_wrapped_result
from enum import StrEnum
from github import Commit as Commit, PullRequest as PullRequest, Repository as Repository
from typing import Any

logger: Incomplete

class CommitFields(StrEnum):
    """Commit fields."""
    SHA = 'sha'
    MESSAGE = 'message'
    AUTHOR_NAME = 'author_name'
    AUTHOR_EMAIL = 'author_email'
    AUTHOR_DATE = 'author_date'
    HTML_URL = 'html_url'
    REPOSITORY = 'repository'
    PR_NUMBER = 'pr_number'
    PR_STATE = 'pr_state'

FIELDS: Incomplete

def get_all_pr_commits_task(self, context_id: str, repository: str, filters: dict) -> None:
    """Get commits from all pull requests in a repository.

    Retrieves and processes commits from all pull requests matching the search criteria.
    Results are stored in cache for future use. This is a Celery task that runs asynchronously.

    Args:
        self: Celery task instance (automatically provided by @shared_task(bind=True)).
        context_id: Authentication context identifier for retrieving GitHub credentials.
        repository: Repository name in format 'owner/repo'.
        filters: Dictionary containing search filters (author, since_date, until_date, fields).

    Returns:
        None. Results are stored in cache.

    Raises:
        Retries the task up to 3 times on failure.
    """
def handle_chord_result(self, result: list[Any], resolved_repos: list[str], filters: SearchFilters, summarize: bool, __timeout__: int) -> tuple[tuple[dict[str, Any], list[str]], list[str]]:
    """Handle the result of a chord task.

    Processes the results from multiple parallel tasks that retrieve PR commits.
    Aggregates cached data from all repositories and formats the final response.

    Args:
        self: Celery task instance (automatically provided by @shared_task(bind=True)).
        result: List of results from all chord tasks (not used in current implementation).
        resolved_repos: List of repository names that were processed.
        filters: Search filters used for the original query.
        summarize: Whether to limit results to first 5 commits.
        __timeout__: Timeout value for the operation.

    Returns:
        Tuple containing:
        - Formatted result dictionary with repositories, commits, and statistics
        - List of callback URLs for notifications

    Raises:
        Exception: If processing is still in progress for any repository.
    """
def get_all_pr_commits_task_chord(self, context_id: str, resolved_repos: list[str], filters: dict, summarize: bool) -> None:
    """Orchestrate parallel processing of PR commits across multiple repositories.

    Creates a chord task that processes multiple repositories in parallel,
    then aggregates the results when all tasks complete.

    Args:
        self: Celery task instance (automatically provided by @shared_task(bind=True)).
        context_id: Authentication context identifier for retrieving GitHub credentials.
        resolved_repos: List of repository names to process in parallel.
        filters: Dictionary containing search filters (author, since_date, until_date, fields).
        summarize: Whether to limit results to first 5 commits.

    Returns:
        None. Creates and executes a chord task that handles the results asynchronously.
    """
