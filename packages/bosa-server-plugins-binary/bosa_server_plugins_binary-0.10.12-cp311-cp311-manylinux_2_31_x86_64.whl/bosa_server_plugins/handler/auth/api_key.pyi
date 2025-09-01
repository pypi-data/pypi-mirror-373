from .schema import AuthenticationSchema as AuthenticationSchema
from bosa_server_plugins.handler.header import HttpHeaders as HttpHeaders

class ApiKeyAuthenticationSchema(AuthenticationSchema):
    """API Key Authentication Schema."""
    HEADER_KEY: str
    @property
    def whitelisted_keys(self) -> list[str]:
        """Get list of whitelisted API keys from environment variable.

        Returns:
            List of whitelisted API keys.
        """
    def is_authenticated(self, headers: HttpHeaders, only_whitelisted: bool = False) -> bool:
        """Checks whether or not the user is authenticated using API Key.

        Args:
            headers: The headers to check.
            only_whitelisted: Whether to only check for whitelisted keys.

        Returns:
            True if the user is authenticated, False otherwise
        """
    def verify_authenticated(self, headers: HttpHeaders, only_whitelisted: bool = False) -> None:
        """Verifies whether or not the user is authenticated using API Key.

        Args:
            headers: The headers to check.
            only_whitelisted: Whether to only check for whitelisted keys.

        Raises:
            UnauthorizedError: If the user is not authenticated
        """
