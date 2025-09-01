from _typeshed import Incomplete
from bosa_server_plugins.auth.scheme import AuthenticationScheme as AuthenticationScheme

class BearerTokenAuthentication(AuthenticationScheme):
    """Bearer authentication for Github."""
    token: Incomplete
    def __init__(self, token: str) -> None:
        """Initialization.

        Args:
            token: The bearer token
        """
    def get_token(self) -> str:
        """The bearer token.

        Returns:
            str: The bearer token
        """
    def to_headers(self) -> dict[str, str]:
        """Converts the authentication scheme to headers to inject into the request.

        Returns:
            dict: Headers to inject into the request
        """
