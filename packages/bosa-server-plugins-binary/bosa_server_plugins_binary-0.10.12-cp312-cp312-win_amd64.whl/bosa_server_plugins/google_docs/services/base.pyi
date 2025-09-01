from bosa_server_plugins.google.services.base import GoogleServiceBase as GoogleServiceBase

class GoogleDocsServiceBase(GoogleServiceBase):
    """Base class for Google Docs services.

    This class provides common functionality for Google Docs services
    """
    name: str
    version: str
    def __init__(self, credentials) -> None:
        """Initialize the Google service with credentials.

        Args:
            credentials (GoogleCredentials): The credentials for the service
        """
