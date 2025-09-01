from _typeshed import Incomplete
from bosa_server_plugins.google.auth.auth import GoogleCredentials as GoogleCredentials
from typing import Any

class GoogleServiceBase:
    """Base class for Google services.

    This class provides common functionality for Google services
    """
    name: str
    version: str
    service: Incomplete
    def __init__(self, credentials: GoogleCredentials) -> None:
        """Initialize the Google service with credentials.

        Args:
            credentials (GoogleCredentials): The credentials for the service
        """
    def filter_none_params(self, params: dict[str, Any]) -> dict[str, Any]:
        """Remove None values from parameters dictionary."""
