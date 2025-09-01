from bosa_server_plugins.google.services.base import GoogleServiceBase as GoogleServiceBase

class GoogleDriveServiceBase(GoogleServiceBase):
    """Base class for Google Drive services.

    This class provides common functionality for Google Drive services
    """
    name: str
    version: str
    def __init__(self, credentials) -> None:
        """Initialize the Google service with credentials.

        Args:
            credentials (GoogleCredentials): The credentials for the service
        """
