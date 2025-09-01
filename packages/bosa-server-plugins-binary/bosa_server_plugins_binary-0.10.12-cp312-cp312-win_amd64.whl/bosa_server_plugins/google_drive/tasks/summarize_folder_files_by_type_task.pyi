from _typeshed import Incomplete
from bosa_server_plugins.cache import CacheService as CacheService
from bosa_server_plugins.common.cache import deserialize_cache_data as deserialize_cache_data, serialize_cache_data as serialize_cache_data
from bosa_server_plugins.common.callback import delete_callback_urls as delete_callback_urls, get_callback_urls as get_callback_urls, with_callbacks as with_callbacks
from bosa_server_plugins.google_drive.constant import GOOGLE_AUTH_CACHE_KEY_FORMAT as GOOGLE_AUTH_CACHE_KEY_FORMAT
from bosa_server_plugins.google_drive.constants.summarize_folder_files import GOOGLE_DRIVE_SUMMARIZE_FOLDER_CACHE_RETRY_COUNT as GOOGLE_DRIVE_SUMMARIZE_FOLDER_CACHE_RETRY_COUNT, GOOGLE_DRIVE_SUMMARIZE_FOLDER_CACHE_RETRY_DELAY_SECONDS as GOOGLE_DRIVE_SUMMARIZE_FOLDER_CACHE_RETRY_DELAY_SECONDS, GOOGLE_DRIVE_SUMMARIZE_FOLDER_TASK_MAX_RETRY as GOOGLE_DRIVE_SUMMARIZE_FOLDER_TASK_MAX_RETRY, GOOGLE_DRIVE_SUMMARIZE_FOLDER_TOTAL_FILES_CACHE_TTL as GOOGLE_DRIVE_SUMMARIZE_FOLDER_TOTAL_FILES_CACHE_TTL, GOOGLE_DRIVE_SUMMARIZE_FOLDER_TOTAL_FILES_PROCESSING_VALUE as GOOGLE_DRIVE_SUMMARIZE_FOLDER_TOTAL_FILES_PROCESSING_VALUE
from bosa_server_plugins.google_drive.helper.summarize_all_files import get_file_type_category as get_file_type_category
from bosa_server_plugins.google_drive.services.files import GoogleDriveFileService as GoogleDriveFileService
from bosa_server_plugins.google_drive.utils.summarize_folder_files import get_summarize_files_cache_key as get_summarize_files_cache_key

logger: Incomplete

def return_folder_summary(email: str, folder_id: str, callback_urls: list[str] | None) -> tuple[dict, list[str]]:
    """Send folder summary to callback URL.

    This task is specifically for sending cached results to callbacks.
    """
def summarize_folder_files_by_type_task(folder_id: str, email: str) -> dict:
    """Summarize all Google Drive files by type in a specific folder including files inside subfolders.

    Not include Google Drive folder.

    Args:
        folder_id: The ID of the folder to summarize
        email: The email of the user

    Returns:
        A dictionary containing the total number of files by type category in the specified folder
    """
