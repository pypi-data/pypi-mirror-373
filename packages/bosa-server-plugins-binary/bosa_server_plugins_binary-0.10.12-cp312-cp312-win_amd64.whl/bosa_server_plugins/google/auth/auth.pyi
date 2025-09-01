from abc import ABC
from bosa_core import ConfigService as ConfigService
from datetime import datetime
from google.oauth2.credentials import Credentials

class GoogleCredentials(ABC):
    """Google authentication scheme."""
    token: str
    refresh_token: str
    expiry: datetime
    config: ConfigService
    def __init__(self, token: str, refresh_token: str, expiry: str, config: ConfigService) -> None:
        """Initialize Google authentication scheme.

        Args:
            token (str): The token
            refresh_token (str): The refresh token
            expiry (str): The expiry date
            config (ConfigService): The config service
        """
    def get_credentials(self) -> Credentials:
        """Get the credentials.

        Returns:
            dict: The credentials
        """
