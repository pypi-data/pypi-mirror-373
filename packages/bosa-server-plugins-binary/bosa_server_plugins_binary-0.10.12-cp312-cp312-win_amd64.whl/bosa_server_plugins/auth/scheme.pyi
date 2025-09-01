import abc
from abc import ABC, abstractmethod

class AuthenticationScheme(ABC, metaclass=abc.ABCMeta):
    """Base authentication scheme."""
    @abstractmethod
    def get_token(self) -> str:
        """Get the token.

        Returns:
            str: The token
        """
    @abstractmethod
    def to_headers(self) -> dict[str, str]:
        """Converts the authentication scheme to headers to inject into the request.

        Returns:
            dict: Headers to inject into the request
        """
