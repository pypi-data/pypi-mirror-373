from bosa_server_plugins.github.gql.common import construct_page_query as construct_page_query
from bosa_server_plugins.github.http.cursor_meta import GithubApiCursorMeta as GithubApiCursorMeta
from datetime import datetime
from pydantic import BaseModel
from typing import Any, ClassVar, Generic, Literal, TypeVar

T = TypeVar('T')
PROJECT_FRAGMENT: str
PROJECT_ITEM_FRAGMENT: str
CONTENTLESS_PROJECT_ITEM_FRAGMENT: str
GQL_PROJECT_LIST_QUERY: str

class GQLProjectBasic(BaseModel):
    """Basic project model."""
    id: str
    number: int
    title: str
    url: str
    @classmethod
    def from_dict(cls, data: dict) -> GQLProjectBasic:
        """Create a GQLProjectBasic from a dictionary.

        Args:
            data: The dictionary to create the project from.

        Returns:
            GQLProjectBasic: The created project.
        """

class GQLProjectItemFieldValue(BaseModel, Generic[T]):
    """Project item field value model."""
    name: str
    value: T | None
    field_type: Literal['single_select', 'text', 'date', 'number']

class GQLProjectItemFieldSingleSelectValue(GQLProjectItemFieldValue[str]):
    """Single select field value."""
    FIELD_TYPE: ClassVar[Literal['single_select']]
    field_type: Literal['single_select']
    option_id: str

class GQLProjectItemFieldTextValue(GQLProjectItemFieldValue[str]):
    """Text field value."""
    FIELD_TYPE: ClassVar[Literal['text']]
    field_type: Literal['text']

class GQLProjectItemFieldDateValue(GQLProjectItemFieldValue[datetime]):
    """Date field value."""
    FIELD_TYPE: ClassVar[Literal['date']]
    field_type: Literal['date']

class GQLProjectItemFieldNumberValue(GQLProjectItemFieldValue[float]):
    """Number field value."""
    FIELD_TYPE: ClassVar[Literal['number']]
    field_type: Literal['number']

class GQLProjectItemBasic(BaseModel):
    """Basic project item model."""
    id: str
    type: str
    created_at: datetime
    updated_at: datetime
    field_values: list[GQLProjectItemFieldSingleSelectValue | GQLProjectItemFieldTextValue | GQLProjectItemFieldDateValue | GQLProjectItemFieldNumberValue]
    @classmethod
    def from_dict(cls, data: dict) -> GQLProjectItemBasic:
        """Create a GQLProjectItemBasic from a dictionary.

        Args:
            data: The dictionary to create the project item from.

        Returns:
            GQLProjectItemBasic: The created project item.
        """

class ProjectData(BaseModel):
    """Project data model for formatted project responses."""
    number: int
    title: str
    description: str | None
    resource_path: str | None
    closed: bool
    owner: str
    creator: str | None
    public: bool

class GQLProjectListResponse(BaseModel):
    """Response model for project list queries."""
    data: list[ProjectData]
    meta: GithubApiCursorMeta
    @classmethod
    def from_dict(cls, data: dict[str, Any], cursor_item_per_page: int) -> GQLProjectListResponse:
        """Create a GQLProjectResponse from a dictionary.

        Transforms the GitHub projects API response into a client-friendly format with
        standardized field names and structure.

        Args:
            data: The dictionary containing GitHub API response with projects data

        Returns:
            GQLProjectResponse: The formatted project response
        """

def get_project_list_query(cursor: str | None, from_last: bool | None, per_page: int | None) -> str:
    """Build the projects list GraphQL query with pagination parameters.

    Args:
        cursor: Cursor pointing to after which element to fetch
        from_last: If True, fetch from the last element
        per_page: Number of elements to fetch per page

    Returns:
        The complete GraphQL query string
    """
