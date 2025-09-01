import abc
from _typeshed import Incomplete
from abc import ABC, abstractmethod
from bosa_server_plugins.auth.scheme import AuthenticationScheme as AuthenticationScheme
from bosa_server_plugins.cache import CacheService as CacheService
from bosa_server_plugins.github.entities.project import Project as Project, ProjectItem as ProjectItem, ProjectListMeta as ProjectListMeta
from bosa_server_plugins.github.gql.project import GQLProjectItemFieldValue as GQLProjectItemFieldValue, GQLProjectListResponse as GQLProjectListResponse, PROJECT_ITEM_FRAGMENT as PROJECT_ITEM_FRAGMENT, get_project_list_query as get_project_list_query
from bosa_server_plugins.github.helper.common import parse_date as parse_date
from bosa_server_plugins.github.helper.connect import query_github_gql as query_github_gql
from enum import Enum
from pydantic import BaseModel, RootModel
from typing import Any, Literal

GITHUB_PROJECTS_CACHE_KEY: str
DEFAULT_TTL: int
PROJECT_ITEMS_QUERY: Incomplete

class FilterType(str, Enum):
    """Filter type enum for discriminated union."""
    DATE_RANGE = 'date_range'
    STRING = 'string'
    STRING_LIST = 'string_list'
    NUMBER = 'number'
    NUMBER_LIST = 'number_list'
    NUMBER_RANGE = 'number_range'

class BaseCustomFieldFilter(BaseModel, ABC, metaclass=abc.ABCMeta):
    """Base class for all custom field filters."""
    field_name: str
    @abstractmethod
    def apply(self, item: ProjectItem) -> bool:
        """Apply the filter to the item.

        Args:
            item: The item to apply the filter to.

        Returns:
            True if the item passes the filter, False otherwise.
        """

class DateRangeFilter(BaseCustomFieldFilter):
    """Filter items by a date range.

    Args:
        from_date: Start date of the range
        to_date: End date of the range
    """
    type: Literal[FilterType.DATE_RANGE]
    from_date: str | None
    to_date: str | None
    def apply(self, item: ProjectItem) -> bool:
        """Apply the filter to the item.

        Args:
            item: The item to apply the filter to.
        """

class StringFilter(BaseCustomFieldFilter):
    """Filter items by string value."""
    type: Literal[FilterType.STRING]
    value: str
    ignore_case: bool | None
    def apply(self, item: ProjectItem) -> bool:
        """Apply the filter to the item.

        Args:
            item: The item to apply the filter to.
        """

class StringListFilter(BaseCustomFieldFilter):
    """Filter items by a list of string values."""
    type: Literal[FilterType.STRING_LIST]
    values: list[str]
    ignore_case: bool | None
    def apply(self, item: ProjectItem) -> bool:
        """Apply the filter to the item.

        Args:
            item: The item to apply the filter to.
        """

class NumberFilter(BaseCustomFieldFilter):
    """Filter items by a number.

    Args:
        value: Value to filter by
    """
    type: Literal[FilterType.NUMBER]
    value: float
    def apply(self, item: ProjectItem) -> bool:
        """Apply the filter to the item.

        Args:
            item: The item to apply the filter to.
        """

class NumberListFilter(BaseCustomFieldFilter):
    """Filter items by a list of numbers.

    Args:
        values: List of values to filter by
    """
    type: Literal[FilterType.NUMBER_LIST]
    values: list[float]
    def apply(self, item: ProjectItem) -> bool:
        """Apply the filter to the item.

        Args:
            item: The item to apply the filter to.
        """

class NumberRangeFilter(BaseCustomFieldFilter):
    """Filter items by a number range. If none of the value is provided, will always return True.

    Args:
        from_value: Start value of the range. If not provided, will ignore the lower bound.
        to_value: End value of the range. If not provided, will ignore the upper bound.
    """
    type: Literal[FilterType.NUMBER_RANGE]
    from_value: float | None
    to_value: float | None
    def apply(self, item: ProjectItem) -> bool:
        """Apply the filter to the item.

        Args:
            item: The item to apply the filter to.

        Returns:
            True if the item passes the filter, False otherwise.
            Will always return True if both from_value and to_value are not provided.
        """

FilterUnion: Incomplete

class CustomFieldFilter(RootModel[FilterUnion]):
    '''Root model for all filter types that uses discriminated union.

    This class uses the \'type\' field to determine which filter to instantiate.
    Example usage in a request:

    ```json
    {
      "filters": [
        {
          "type": "date_range",
          "field_name": "due_date",
          "from_date": "2023-01-01T00:00:00Z",
          "to_date": "2023-12-31T23:59:59Z"
        },
        {
          "type": "string_list",
          "field_name": "status",
          "values": ["open", "in progress"]
        }
      ]
    }
    ```
    '''
    def apply(self, item: ProjectItem) -> bool:
        """Apply the filter to the item."""
    @property
    def field_name(self) -> str:
        """Get the field name."""
FilterTypes = DateRangeFilter | StringFilter | StringListFilter | NumberFilter | NumberListFilter | NumberRangeFilter

class ProjectSummaryField(BaseModel):
    """Project summary field."""
    field_name: str
    summaries: dict[str, Any]

class ProjectSummary(BaseModel):
    """Project summary."""
    total_items: int
    summary_fields: list[ProjectSummaryField]

def get_items_from_project(organization: str, number: int, auth_scheme: AuthenticationScheme, force_new: bool = False, *, status: str | None = None, type_: str | None = None, page: int = 1, per_page: int = 30, cache_service: CacheService, created_at_from: str | None = None, created_at_to: str | None = None, updated_at_from: str | None = None, updated_at_to: str | None = None, custom_fields_filter: list[FilterTypes] | None = None, summarize: bool = False) -> list[ProjectItem] | ProjectSummary:
    """Get items from a GitHub Project V2.

    Args:
        organization: Organization name
        number: Project number
        auth_scheme: Authentication Scheme
        force_new: If True, bypass cache and fetch new data
        status: Optional status to filter items by
        type_: Optional type to filter items by
        page: Page number (1-based)
        per_page: Number of items per page
        cache_service: Cache service
        created_at_from: Optional start date to filter items by
        created_at_to: Optional end date to filter items by
        updated_at_from: Optional start date to filter items by
        updated_at_to: Optional end date to filter items by
        summarize: If True, only output the summary of the project
        custom_fields_filter: Optional list of custom field filters
    Returns:
        List of project items or project summary if summarize is True
    """
def get_projects_list(auth_scheme: AuthenticationScheme, organization: str, cache_service: CacheService = None, force_new: bool = False, *, query: str | None = None, min_permission_level: str | None = None, order_by: str | None = None, direction: str | None = None, per_page: int | None = 10, cursor: str | None = None, from_last: bool | None = False) -> tuple[list[Project], ProjectListMeta]:
    """Get list of projects from a GitHub Organization.

    This function retrieves projects and uses helper functions to handle caching,
    API communication, and response formatting.

    Args:
        auth_scheme: Authentication Scheme
        organization: Organization name
        query: Query to search for (Project name/string)
        min_permission_level: Minimum permission level as string
        order_by: Field to order by
        direction: Direction to order by
        per_page: Number of items per page
        cursor: Cursor to start from
        from_last: If True, fetch from the last item
        cache_service: Cache service for caching results
        force_new: If True, bypass cache and fetch new data
    Returns:
        A tuple containing:
        - List of Project objects
        - ProjectListMeta object with pagination info and metadata
    """
