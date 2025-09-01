from _typeshed import Incomplete
from bosa_server_plugins.cache.interface import CacheService as CacheService
from bosa_server_plugins.common.mimetypes import MimeTypes as MimeTypes
from bosa_server_plugins.google.services.user_info import GoogleUserInfoService as GoogleUserInfoService
from bosa_server_plugins.google_drive.services.files import GoogleDriveFileService as GoogleDriveFileService
from fastapi import BackgroundTasks as BackgroundTasks

GOOGLE_DRIVE_SUMMARIZE_TOTAL_FILES_BY_TYPE_CACHE_KEY: str
GOOGLE_DRIVE_SUMMARIZE_TOTAL_FILES_BY_TYPE_CACHE_TTL: int
GOOGLE_DRIVE_SUMMARIZE_TOTAL_FILES_BY_TYPE_PROCESSING_VALUE: str
MIMETYPE_TO_FILE_TYPE: Incomplete

def summarize_total_files_by_type(file_service: GoogleDriveFileService, user_info_service: GoogleUserInfoService, cache_service: CacheService = None, background_tasks: BackgroundTasks = None) -> dict:
    """Summarize total files by type in Google Drive.

    Not include Google Drive folder.

    Args:
        request: The request object
        file_service: GoogleDriveFileService instance
        user_info_service: GoogleUserInfoService instance
        cache_service: CacheService instance
        background_tasks: FastAPI background tasks for async processing

    Returns:
        A dictionary containing the total number of files by type category in My Drive, Shared with Me, and combined;
        or total number of files by type category in a specific folder if request.folder_id is provided.
    """
def get_file_type_category(mime_type: str) -> str:
    """Get the standardized file type category from a MIME type.

    Args:
        mime_type: The MIME type string

    Returns:
        A standardized file type category or 'other' if the MIME type is not recognized
    """
