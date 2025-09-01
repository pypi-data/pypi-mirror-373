from _typeshed import Incomplete
from bosa_server_plugins.auth.scheme import AuthenticationScheme as AuthenticationScheme
from bosa_server_plugins.cache import CacheService as CacheService
from bosa_server_plugins.github.gql.common import to_datetime_string as to_datetime_string
from bosa_server_plugins.github.helper.connect import query_github_gql as query_github_gql
from enum import Enum

PER_PAGE_REQUEST: int
CACHE_TTL: Incomplete

class FragmentTypes(str, Enum):
    """Fragment types for GitHub GraphQL API."""
    COMMIT = 'commit'
    ISSUE = 'issue'
    PULL_REQUEST = 'pull_request'
    PULL_REQUEST_REVIEW = 'pull_request_review'

query: str
pagination_query: str
commit_fragment: str
commit_pagination_fragment: str
issue_fragment: str
issue_pagination_fragment: str
pull_request_fragment: str
pull_request_pagination_fragment: str
pull_request_review_fragment: str
pull_request_review_pagination_fragment: str
fragments_map: Incomplete
pagination_fragments_map: Incomplete

def get_user_contributions(auth_scheme: AuthenticationScheme, cache_service: CacheService, *, login: str, since: str, until: str, requested_fragments: list[FragmentTypes], organization_id: str = None) -> dict:
    """Fetch user contributions from GitHub GraphQL API.

    This function fetches user contributions data for the specified fragments.
    It handles pagination automatically for any contribution type that exceeds
    the per-page limit.

    Args:
        auth_scheme: Authentication scheme for GitHub API
        cache_service: Cache service for storing fetched data
        login: GitHub username
        since: ISO-8601 formatted start date
        until: ISO-8601 formatted end date
        requested_fragments: List of contribution types to fetch
            (commit, issue, pull_request, pull_request_review)
        organization_id: Organization ID to filter contributions by organization

    Returns:
        Dictionary containing the combined contribution data
    """
