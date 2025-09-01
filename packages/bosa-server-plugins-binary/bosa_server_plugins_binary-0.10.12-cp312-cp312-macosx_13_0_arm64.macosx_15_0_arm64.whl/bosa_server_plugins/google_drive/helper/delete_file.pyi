from bosa_server_plugins.google_drive.requests.files import DeleteFileRequest as DeleteFileRequest
from bosa_server_plugins.google_drive.services.files import GoogleDriveFileService as GoogleDriveFileService

def delete_file(request: DeleteFileRequest, service: GoogleDriveFileService):
    """Delete a file or folder from Google Drive.

    Args:
        request: The request object containing file ID and options
        service: GoogleDriveFileService instance
    """
