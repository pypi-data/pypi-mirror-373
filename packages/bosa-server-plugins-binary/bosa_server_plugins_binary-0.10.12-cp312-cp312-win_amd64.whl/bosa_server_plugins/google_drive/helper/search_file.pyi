from bosa_server_plugins.google_drive.requests.files import SearchFileRequest as SearchFileRequest
from bosa_server_plugins.google_drive.services.files import GoogleDriveFileService as GoogleDriveFileService

def search_files(request: SearchFileRequest, service: GoogleDriveFileService):
    """List files from Google Drive.

    Args:
        request: The request object
        service: GoogleDriveFileService instance
    """
