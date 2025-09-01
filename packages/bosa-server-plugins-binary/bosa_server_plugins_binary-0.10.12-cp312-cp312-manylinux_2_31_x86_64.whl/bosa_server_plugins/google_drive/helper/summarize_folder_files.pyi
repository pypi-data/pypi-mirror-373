from _typeshed import Incomplete
from bosa_server_plugins.background_task.utils import is_worker_available as is_worker_available
from bosa_server_plugins.cache.interface import CacheService as CacheService
from bosa_server_plugins.common.cache import deserialize_cache_data as deserialize_cache_data
from bosa_server_plugins.common.callback import save_callback_urls as save_callback_urls, with_callbacks as with_callbacks
from bosa_server_plugins.google.auth.auth import GoogleCredentials as GoogleCredentials
from bosa_server_plugins.google.services.user_info import GoogleUserInfoService as GoogleUserInfoService
from bosa_server_plugins.google_drive.constant import GOOGLE_AUTH_CACHE_KEY_FORMAT as GOOGLE_AUTH_CACHE_KEY_FORMAT, GOOGLE_AUTH_CACHE_TTL as GOOGLE_AUTH_CACHE_TTL
from bosa_server_plugins.google_drive.constants.summarize_folder_files import GOOGLE_DRIVE_SUMMARIZE_FOLDER_TOTAL_FILES_PROCESSING_VALUE as GOOGLE_DRIVE_SUMMARIZE_FOLDER_TOTAL_FILES_PROCESSING_VALUE
from bosa_server_plugins.google_drive.requests.files import GetFolderTotalFileByTypeSummaryRequest as GetFolderTotalFileByTypeSummaryRequest
from bosa_server_plugins.google_drive.tasks.summarize_folder_files_by_type_task import summarize_folder_files_by_type_task as summarize_folder_files_by_type_task
from bosa_server_plugins.google_drive.utils.summarize_folder_files import get_summarize_files_cache_key as get_summarize_files_cache_key

logger: Incomplete

def summarize_folder_total_files_by_type(request: GetFolderTotalFileByTypeSummaryRequest, auth_scheme: GoogleCredentials, cache_service: CacheService = None) -> dict:
    """Summarize total files by type in Google Drive.

    Not include Google Drive folder.

    Args:
        request: The request object
        auth_scheme: GoogleCredentials instance
        cache_service: CacheService instance

    Returns:
        A dictionary containing the total number of files in a specific folder including files inside subfolders.
    """
