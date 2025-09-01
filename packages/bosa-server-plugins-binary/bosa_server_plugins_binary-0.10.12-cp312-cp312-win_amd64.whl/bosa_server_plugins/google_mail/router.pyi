from bosa_server_plugins.auth.scheme import AuthenticationScheme as AuthenticationScheme
from bosa_server_plugins.google.router import GoogleApiRoutes as GoogleApiRoutes
from bosa_server_plugins.google_mail.routes.attachments import GoogleMailAttachmentsRoutes as GoogleMailAttachmentsRoutes
from bosa_server_plugins.google_mail.routes.auto_reply import GoogleMailAutoReplyRoutes as GoogleMailAutoReplyRoutes
from bosa_server_plugins.google_mail.routes.drafts import GoogleMailDraftsRoutes as GoogleMailDraftsRoutes
from bosa_server_plugins.google_mail.routes.emails import GoogleMailEmailsRoutes as GoogleMailEmailsRoutes
from bosa_server_plugins.google_mail.routes.labels import GoogleMailLabelsRoutes as GoogleMailLabelsRoutes
from bosa_server_plugins.google_mail.routes.threads import GoogleMailThreadsRoutes as GoogleMailThreadsRoutes
from bosa_server_plugins.handler.router import Router as Router

class GoogleMailApiRoutes(GoogleApiRoutes):
    """Google Mail API Routes."""
    INTEGRATION_NAME: str
    router: Router
