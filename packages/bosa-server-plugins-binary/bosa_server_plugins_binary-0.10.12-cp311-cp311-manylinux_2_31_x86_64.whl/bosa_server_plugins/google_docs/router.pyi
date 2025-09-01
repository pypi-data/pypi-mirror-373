from bosa_server_plugins.google.router import GoogleApiRoutes as GoogleApiRoutes
from bosa_server_plugins.google_docs.routes.comments import GoogleDocsCommentsRoutes as GoogleDocsCommentsRoutes
from bosa_server_plugins.google_docs.routes.documents import GoogleDocsDocumentsRoutes as GoogleDocsDocumentsRoutes

class GoogleDocsApiRoutes(GoogleApiRoutes):
    """Google Docs API Routes."""
