from bosa_server_plugins.handler import BaseRequestModel as BaseRequestModel
from typing import Any

class SqlQueryRequest(BaseRequestModel):
    """The SQL query request."""
    query: str
    variables: dict[str, Any] | None
