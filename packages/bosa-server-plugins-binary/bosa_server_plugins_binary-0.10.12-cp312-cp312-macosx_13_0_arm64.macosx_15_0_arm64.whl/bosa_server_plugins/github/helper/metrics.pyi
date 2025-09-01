from bosa_server_plugins.auth.scheme import AuthenticationScheme as AuthenticationScheme
from bosa_server_plugins.github.helper.connect import send_request_to_github as send_request_to_github
from bosa_server_plugins.github.helper.pagination import create_github_pagination_meta as create_github_pagination_meta
from typing import Any
from typing_extensions import Optional

def get_all_contributor_commit_activity(owner: str, repo: str, auth_scheme: AuthenticationScheme) -> tuple[Any, int]:
    """Get all contributor commit activity for a repository.

    Args:
        owner: The account owner of the repository
        repo: The name of the repository
        auth_scheme: The authentication

    Returns:
        A tuple containing:
        - HTTP status code (200 or 202)
        - List of Contributor objects if status is 200, None if status is 202
    """
def get_repository_contributors(owner: str, repo: str, auth_scheme: AuthenticationScheme, *, anon: Optional[str] = None, per_page: Optional[int] = None, page: Optional[int] = None) -> tuple[list[Any], Any]:
    """Get contributor statistics for a repository.

    Args:
        owner: The account owner of the repository
        repo: The name of the repository
        auth_scheme: The authentication
        anon: Set to '1' or 'true' to include anonymous contributors in results
        per_page: Results per page (max 100)
        page: Page number of the results to fetch

    Returns:
        A tuple containing:
        - List of Contributor objects if status is 200, None if status is 202
        - Pagination metadata
    """
def get_last_year_commit_activity(owner: str, repo: str, auth_scheme: AuthenticationScheme) -> tuple[Any, int]:
    """Get last year commit activity for a repository.

    From Github: Returns the last year of commit activity grouped by `week`.
    The days array is a group of commits per day, starting on `Sunday`.

    Args:
        owner: The account owner of the repository
        repo: The name of the repository
        auth_scheme: The authentication

    Returns:
        A tuple containing:
        - HTTP status code (200 or 202)
        - List of Contributor objects if status is 200, None if status is 202
    """
def get_weekly_commit_count(owner: str, repo: str, auth_scheme: AuthenticationScheme) -> tuple[Any, int]:
    """Get weekly commit count for a repository.

    From Github: Returns the total commit counts for the owner and repository.

    Args:
        owner: The account owner of the repository
        repo: The name of the repository
        auth_scheme: The authentication

    Returns:
        A tuple containing:
        - HTTP status code (200 or 202 or 204)
        - List of Contributor objects if status is 200, None if status is 202
    """
