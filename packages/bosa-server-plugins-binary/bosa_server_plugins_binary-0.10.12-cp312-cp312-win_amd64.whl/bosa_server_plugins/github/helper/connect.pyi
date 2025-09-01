from bosa_server_plugins.auth.scheme import AuthenticationScheme as AuthenticationScheme
from bosa_server_plugins.github.entities.response import GithubAPIResponse as GithubAPIResponse
from bosa_server_plugins.github.gql.common import handle_graphql_error as handle_graphql_error
from gql import Client
from http import HTTPMethod
from typing import Any

DEFAULT_GITHUB_BASE_URL: str
DEFAULT_REQUEST_TIMEOUT: int
DEFAULT_API_VERSION: str

def send_request_to_github(authentication_scheme: AuthenticationScheme, path: str, params: dict, body: dict, method: HTTPMethod = ..., base_url: str = ..., api_version: str = ..., accept: str = 'application/vnd.github+json'):
    '''Send a request to GitHub API.

    Args:
        authentication_scheme: Authentication scheme to use
        path: API path
        params: Query parameters
        body: Request body
        method: HTTP method
        base_url: Base URL for GitHub API
        api_version: GitHub API version
        accept: Accept header, defaults to "application/vnd.github+json"

    Returns:
        Response containing the response data, status code and headers
    '''
def get_github_gql_client(auth_scheme: AuthenticationScheme, custom_headers: dict[str, str] | None = None) -> Client:
    """Get a configured GitHub GraphQL client.

    Args:
        auth_scheme: The Authentication Scheme
        custom_headers: Optional headers for the request

    Returns:
        gql.Client: Configured GraphQL client
    """
def query_github_gql(auth_scheme: AuthenticationScheme, query: str, variables: dict[str, Any] | None = None, headers: dict[str, str] | None = None) -> dict[str, Any]:
    """Query GitHub's GraphQL API using gql.

    Args:
        auth_scheme: The authentication Scheme
        query: The GraphQL query string
        variables: Optional variables for the query
        headers: Optional additional headers for the request

    Returns:
        Dict containing the response data
    """
