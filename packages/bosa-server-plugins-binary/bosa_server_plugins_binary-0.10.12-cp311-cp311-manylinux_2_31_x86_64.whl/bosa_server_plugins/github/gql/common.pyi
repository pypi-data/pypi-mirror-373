from bosa_server_plugins.github.gql.exception import GraphQLError as GraphQLError
from enum import Enum, StrEnum
from graphql import ExecutionResult as ExecutionResult

class GQLDirection(StrEnum):
    """Direction for ordering results."""
    ASC = 'ASC'
    DESC = 'DESC'

class GQLIssueOrderBy(str, Enum):
    """Issue order by model."""
    CREATED_AT = 'CREATED_AT'
    UPDATED_AT = 'UPDATED_AT'
    COMMENTS = 'COMMENTS'

def handle_graphql_error(response: ExecutionResult) -> None:
    """Handle a GraphQL error.

    Args:
        response: The response from the GraphQL query.
    """
def to_datetime_string(date_time: str) -> str:
    """Convert a date or datetime string to a UTC datetime string.

    Args:
        date_time: The date or datetime string in formats like:
                  '2025-02-02' or '2025-02-02T00:00:00' or '2025-02-02T00:00:00Z'

    Returns:
        str: The UTC datetime string in ISO format required by GitHub.
    """
def construct_page_query(from_last: bool, per_page: int, cursor: str) -> str:
    """Construct the page parameters for a GraphQL query.

    Args:
        from_last: If True, fetch from the last item
        per_page: The number of items per page
        cursor: The cursor to start from
    """
