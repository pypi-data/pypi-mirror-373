from bosa_server_plugins.google.auth.auth import GoogleCredentials as GoogleCredentials
from bosa_server_plugins.google.services.user_info import GoogleUserInfoService as GoogleUserInfoService
from bosa_server_plugins.google_docs.requests.comments import ListCommentsRequest as ListCommentsRequest, SummarizeCommentsRequest as SummarizeCommentsRequest
from bosa_server_plugins.google_drive.services.comments import GoogleDriveCommentsService as GoogleDriveCommentsService
from bosa_server_plugins.google_drive.services.files import GoogleDriveFileService as GoogleDriveFileService
from bosa_server_plugins.handler import ExposedDefaultHeaders as ExposedDefaultHeaders, Router as Router
from typing import Callable

class GoogleDocsCommentsRoutes:
    """Google Docs Comments Route."""
    def __init__(self, router: Router, get_auth_scheme: Callable[[ExposedDefaultHeaders], GoogleCredentials]) -> None:
        """Initialize the Google Docs Comments Route.

        Args:
            router: The router to register the routes with.
            get_auth_scheme: A function to get the authentication scheme.
        """
