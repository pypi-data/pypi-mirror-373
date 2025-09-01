from bosa_server_plugins.auth.scheme import AuthenticationScheme as AuthenticationScheme
from bosa_server_plugins.cache import CacheService as CacheService
from bosa_server_plugins.github.helper.connect import query_github_gql as query_github_gql

def get_organization_node_id_from_name(auth_scheme: AuthenticationScheme, cache_service: CacheService, organization_name: str) -> str:
    """Get the organization ID from the organization name.

    Args:
        auth_scheme (AuthenticationScheme): The authentication scheme.
        cache_service (CacheService): The cache service
        organization_name (str): The name of the organization.

    Returns:
        str: The organization ID.
    """
