from bosa_server_plugins.auth.scheme import AuthenticationScheme as AuthenticationScheme
from bosa_server_plugins.github.helper.connect import send_request_to_github as send_request_to_github

def create_github_pagination_meta(link_header_pages: dict, per_page: int, current_page: int, current_page_total_data: int, path: str, params: dict, auth_scheme: AuthenticationScheme, *, body: dict | None = None, method=...) -> dict:
    """Create pagination meta for github response.

    Args:
        link_header_pages: Pages dictionary from Link Header
        per_page: Number of items per page
        current_page: Current page number
        current_page_total_data: Total data in current page
        path: Path of the request
        params: Request parameters
        auth_scheme: Authentication scheme
        body: Request body
        method: HTTP method

    Returns:
        Dictionary containing pagination meta
    """
