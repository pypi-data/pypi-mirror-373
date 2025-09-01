from bosa_server_plugins.google_drive.requests.files import CreateFileRequest as CreateFileRequest, CreateFolderRequest as CreateFolderRequest
from bosa_server_plugins.google_drive.services.files import GoogleDriveFileService as GoogleDriveFileService

def create_file(request: CreateFileRequest, service: GoogleDriveFileService):
    """Upload a file to Google Drive from a file upload.

    Args:
        request: The request object
        service: GoogleDriveFileService instance
    """
def create_folder(request: CreateFolderRequest, service: GoogleDriveFileService):
    """Create a folder in Google Drive.

    Args:
        request: The request object
        service: GoogleDriveFileService instance
    """
