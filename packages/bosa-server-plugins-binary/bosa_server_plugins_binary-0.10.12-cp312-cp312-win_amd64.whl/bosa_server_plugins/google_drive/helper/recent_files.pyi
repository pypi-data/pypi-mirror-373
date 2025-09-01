from bosa_server_plugins.google_drive.services.files import GoogleDriveFileService as GoogleDriveFileService
from enum import StrEnum

class TimestampField(StrEnum):
    """Enum for timestamp fields used in Google Drive file metadata."""
    MODIFIED_BY_ME_TIME = 'modifiedByMeTime'
    VIEWED_BY_ME_TIME = 'viewedByMeTime'

def recent_files(service: GoogleDriveFileService):
    """Update a file in Google Drive.

    Args:
        service: GoogleDriveFileService instance
    """
