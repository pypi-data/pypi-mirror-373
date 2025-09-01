from bosa_server_plugins.github.constant import BASE_API_GITHUB_URL as BASE_API_GITHUB_URL, CURRENT_API_VERSION as CURRENT_API_VERSION, DEFAULT_TIMEOUT as DEFAULT_TIMEOUT

def revoke_github_access_token(token: str):
    """Revokes the Github access token.

    Args:
        token: The token.
    """
