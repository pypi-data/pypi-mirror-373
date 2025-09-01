from bosa_server_plugins.google.router import GoogleApiRoutes as GoogleApiRoutes
from bosa_server_plugins.google_drive.routes.download import GoogleDriveDownloadRoutes as GoogleDriveDownloadRoutes
from bosa_server_plugins.google_drive.routes.files import GoogleDriveFilesRoutes as GoogleDriveFilesRoutes
from bosa_server_plugins.google_drive.routes.permissions import GoogleDrivePermissionsRoutes as GoogleDrivePermissionsRoutes

class GoogleDriveApiRoutes(GoogleApiRoutes):
    """Google Drive API Routes."""
    INTEGRATION_NAME: str
