import abc
from abc import ABC, abstractmethod
from bosa_server_plugins.handler.header import HttpHeaders as HttpHeaders

class AuthenticationSchema(ABC, metaclass=abc.ABCMeta):
    """Basic authentication schema."""
    @abstractmethod
    def is_authenticated(self, headers: HttpHeaders, only_whitelisted: bool = False) -> bool:
        """Checks whether or not the user is authenticated using API Key.

        Args:
            headers: The headers to check.
            only_whitelisted: Whether to only check for whitelisted keys.

        Returns:
            True if the user is authenticated, False otherwise
        """
    @abstractmethod
    def verify_authenticated(self, headers: HttpHeaders, only_whitelisted: bool = False) -> None:
        """Verifies whether or not the user is authenticated using API Key.

        Args:
            headers: The headers to check.
            only_whitelisted: Whether to only check for whitelisted keys.

        Raises:
            UnauthorizedError: If the user is not authenticated
        """
