from bosa_server_plugins.auth.scheme import AuthenticationScheme as AuthenticationScheme
from bosa_server_plugins.github.entities.response import GithubAPIResponse as GithubAPIResponse
from bosa_server_plugins.github.helper.connect import send_request_to_github as send_request_to_github
from enum import Enum

class SearchType(Enum):
    """Search type of github search."""
    IS_ISSUE = 'is:issue'
    IS_PR = 'is:pr'

def github_search(query: str, search_type: SearchType, auth_scheme: AuthenticationScheme, *, sort: str | None = None, order: str | None = None, page: int | None = None, per_page: int | None = None) -> GithubAPIResponse:
    """Search for issues or pull requests on Github.

    Args:
        query: The search query.
        search_type: The type of search.
        auth_scheme: The authentication scheme.
        sort: The sort order.
        order: The order of the results.
        page: The page number.
        per_page: The number of results per page.

    Returns:
        GithubAPIResponse containing the search results.
    """
