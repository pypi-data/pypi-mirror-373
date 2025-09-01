from bosa_server_plugins.sql.service.url import SqlUrlService as SqlUrlService
from sqlalchemy.engine import Engine as Engine
from typing import Any

def query_sql(db_url_string: str, query: str, variables: dict[str, Any] | None = None) -> list | dict:
    '''Executes a SQL query using SQLAlchemy with protection against SQL injection.

    Args:
        db_url_string: Database URL connection string
        query: SQL query with named parameters (e.g., "SELECT * FROM users WHERE id = :user_id")
        variables: Dictionary of parameter values to bind to the query

    Returns:
        Query results as a list of dictionaries for SELECT queries,
        or affected row count for INSERT/UPDATE/DELETE queries

    Raises:
        SQLAlchemyError: If there\'s an error with the database operation
        ValueError: If the query or variables are invalid
    '''
