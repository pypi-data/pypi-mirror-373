from bosa_server_plugins.google_drive.requests.files import GetFileRequest as GetFileRequest
from bosa_server_plugins.google_drive.services.files import GoogleDriveFileService as GoogleDriveFileService

def get_file(request: GetFileRequest, service: GoogleDriveFileService):
    """Get a file from Google Drive by ID.

    Args:
        request: The request object
        service: GoogleDriveFileService instance
    """
