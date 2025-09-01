from bosa_server_plugins.google_drive.requests.files import UpdateFileRequest as UpdateFileRequest, UpdateFolderRequest as UpdateFolderRequest
from bosa_server_plugins.google_drive.services.files import GoogleDriveFileService as GoogleDriveFileService

def update_file(request: UpdateFileRequest, service: GoogleDriveFileService):
    """Update a file in Google Drive.

    Args:
        request: The request object
        service: GoogleDriveFileService instance
    """
def update_folder(request: UpdateFolderRequest, service: GoogleDriveFileService):
    """Update a folder in Google Drive.

    Args:
        request: The request object
        service: GoogleDriveFileService instance
    """
