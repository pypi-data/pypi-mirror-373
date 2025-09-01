from _typeshed import Incomplete
from bosa_server_plugins.google.plugin import GoogleApiPlugin as GoogleApiPlugin
from bosa_server_plugins.google_mail.router import GoogleMailApiRoutes as GoogleMailApiRoutes

class GoogleMailApiPlugin(GoogleApiPlugin):
    """Google Mail API Plugin."""
    CACHE_STATE_PREFIX: str
    name: str
    version: str
    description: str
    scope: Incomplete
    client_config: Incomplete
    def __init__(self) -> None:
        """Initializes the plugin."""
