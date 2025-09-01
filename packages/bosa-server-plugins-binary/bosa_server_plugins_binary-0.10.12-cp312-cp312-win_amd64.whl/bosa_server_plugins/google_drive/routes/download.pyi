from bosa_server_plugins.google.auth.auth import GoogleCredentials as GoogleCredentials
from bosa_server_plugins.google_drive.requests.download import DownloadFileRequest as DownloadFileRequest
from bosa_server_plugins.google_drive.services.download import GoogleDriveDownloadService as GoogleDriveDownloadService
from bosa_server_plugins.google_drive.services.files import GoogleDriveFileService as GoogleDriveFileService
from bosa_server_plugins.handler import ExposedDefaultHeaders as ExposedDefaultHeaders, Router as Router
from bosa_server_plugins.handler.decorators import exclude_from_mcp as exclude_from_mcp
from typing import Callable

class GoogleDriveDownloadRoutes:
    """Google Drive Files Route."""
    def __init__(self, router: Router, get_auth_scheme: Callable[[ExposedDefaultHeaders], GoogleCredentials]) -> None:
        """Initialize Google Drive download routes.

        Args:
            router: Router instance
            get_auth_scheme: Function to get the authentication scheme
        """
