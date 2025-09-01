from _typeshed import Incomplete
from bosa_server_plugins.cache import CacheService as CacheService
from bosa_server_plugins.google.auth.auth import GoogleCredentials as GoogleCredentials
from bosa_server_plugins.google.services.user_info import GoogleUserInfoService as GoogleUserInfoService
from bosa_server_plugins.google_drive.requests.files import CopyFileRequest as CopyFileRequest, CreateFileRequest as CreateFileRequest, CreateFolderRequest as CreateFolderRequest, DeleteFileRequest as DeleteFileRequest, GetFileRequest as GetFileRequest, GetFolderTotalFileByTypeSummaryRequest as GetFolderTotalFileByTypeSummaryRequest, SearchFileRequest as SearchFileRequest, UpdateFileRequest as UpdateFileRequest, UpdateFolderRequest as UpdateFolderRequest
from bosa_server_plugins.google_drive.services.files import GoogleDriveFileService as GoogleDriveFileService
from bosa_server_plugins.handler import BaseRequestModel as BaseRequestModel, ExposedDefaultHeaders as ExposedDefaultHeaders, Router as Router
from fastapi import BackgroundTasks as BackgroundTasks
from typing import Callable

class GoogleDriveFilesRoutes:
    """Google Drive Files Route."""
    cache: Incomplete
    def __init__(self, router: Router, get_auth_scheme: Callable[[ExposedDefaultHeaders], GoogleCredentials], cache: CacheService) -> None:
        """Initialize Google Drive files routes.

        Args:
            router: Router instance
            get_auth_scheme: Function to get the authentication scheme
            cache: CacheService instance
        """
