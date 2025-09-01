from bosa_server_plugins.google.auth.auth import GoogleCredentials as GoogleCredentials
from bosa_server_plugins.google_drive.requests.permissions import CreatePermissionRequest as CreatePermissionRequest, DeletePermissionRequest as DeletePermissionRequest, GetPermissionRequest as GetPermissionRequest, ListPermissionRequest as ListPermissionRequest, UpdatePermissionRequest as UpdatePermissionRequest
from bosa_server_plugins.google_drive.services.files import GoogleDriveFileService as GoogleDriveFileService
from bosa_server_plugins.google_drive.services.permissions import GoogleDrivePermissionsService as GoogleDrivePermissionsService
from bosa_server_plugins.handler import ExposedDefaultHeaders as ExposedDefaultHeaders, Router as Router
from typing import Callable

class GoogleDrivePermissionsRoutes:
    """Google Drive Permissions Route."""
    def __init__(self, router: Router, get_auth_scheme: Callable[[ExposedDefaultHeaders], GoogleCredentials]) -> None:
        """Initialize Google Drive permissions routes.

        Args:
            router: Router instance
            get_auth_scheme: Function to get the authentication scheme
        """
