from bosa_server_plugins.google.auth.auth import GoogleCredentials as GoogleCredentials
from bosa_server_plugins.google_docs.requests.copy import CopyRequest as CopyRequest
from bosa_server_plugins.google_docs.requests.documents import BatchUpdateDocumentRequest as BatchUpdateDocumentRequest, CreateDocumentRequest as CreateDocumentRequest, GetDocumentRequest as GetDocumentRequest, GetListDocumentsRequest as GetListDocumentsRequest, UpdateDocumentMarkdownRequest as UpdateDocumentMarkdownRequest
from bosa_server_plugins.google_docs.services.documents import GoogleDocsDocumentsService as GoogleDocsDocumentsService
from bosa_server_plugins.google_drive.services.files import GoogleDriveFileService as GoogleDriveFileService
from bosa_server_plugins.handler import ExposedDefaultHeaders as ExposedDefaultHeaders, Router as Router
from typing import Callable

class GoogleDocsDocumentsRoutes:
    """Google Docs Document Route."""
    def __init__(self, router: Router, get_auth_scheme: Callable[[ExposedDefaultHeaders], GoogleCredentials]) -> None:
        """Initialize the Google Docs Document Route."""
