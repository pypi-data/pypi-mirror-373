from bosa_server_plugins.google.auth.auth import GoogleCredentials as GoogleCredentials
from bosa_server_plugins.google.services.base import GoogleServiceBase as GoogleServiceBase

class GoogleAdminServiceBase(GoogleServiceBase):
    """Base class for Google Admin SDK services.

    This class provides common functionality for Google Admin SDK services
    """
    name: str
    def __init__(self, credentials: GoogleCredentials) -> None:
        """Initialize the Google service with credentials.

        Args:
            credentials (GoogleCredentials): The credentials for the service
        """
