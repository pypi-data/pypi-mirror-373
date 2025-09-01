from _typeshed import Incomplete
from bosa_server_plugins.handler import ExposedDefaultHeaders as ExposedDefaultHeaders, Router as Router
from bosa_server_plugins.sql.requests import SqlQueryRequest as SqlQueryRequest
from bosa_server_plugins.sql.service.query import query_sql as query_sql
from typing import Callable

class SqlQueryRoutes:
    """SQL Query Routes."""
    router: Router
    get_active_integration: Incomplete
    def __init__(self, router: Router, get_active_integration: Callable[[ExposedDefaultHeaders], str]) -> None:
        """Initializes the routes.

        Args:
            router (Router): The router instance.
            get_active_integration (Callable[[ExposedDefaultHeaders], str]): The function to get the active integration.
        """
