from bosa_server_plugins.github.gql.project import GQLProjectItemFieldDateValue as GQLProjectItemFieldDateValue, GQLProjectItemFieldNumberValue as GQLProjectItemFieldNumberValue, GQLProjectItemFieldSingleSelectValue as GQLProjectItemFieldSingleSelectValue, GQLProjectItemFieldTextValue as GQLProjectItemFieldTextValue, GQLProjectItemFieldValue as GQLProjectItemFieldValue
from bosa_server_plugins.github.helper.common import parse_date as parse_date
from pydantic import BaseModel
from typing import Any

class Content(BaseModel):
    """Content of a project item."""
    title: str
    body: str | None
    number: int | None
    state: str | None
    url: str | None
    labels: list[str]
    assignees: list[str]
    milestone: str | None
    repository: str | None
    def __post_init__(self) -> None:
        """Initialize default values for lists."""
    @classmethod
    def from_github(cls, data: dict) -> Content:
        """Create Content from GitHub API response.

        Args:
            data: GitHub API response for content

        Returns:
            Content instance
        """
    @classmethod
    def from_dict(cls, data: dict) -> Content:
        """Creates from dictionary.

        Args:
            data: The data in dictionary to be mapped 1:1

        Returns:
            The Content reconstructed from dict
        """

class ProjectItem(BaseModel):
    """Project item."""
    id: str
    type: str
    title: str
    status: str
    content: Content
    field_values: list[GQLProjectItemFieldValue]
    created_at: str
    updated_at: str
    def model_dump(self, **kwargs):
        """Custom model_dump to properly serialize field values.

        Returns:
            dict: Dictionary representation of this model
        """
    @classmethod
    def from_github(cls, data: dict) -> ProjectItem:
        """Create Item from GitHub API response.

        Args:
            data: GitHub API response for an item

        Returns:
            Item instance
        """
    @classmethod
    def from_dict(cls, data: dict) -> ProjectItem:
        """Creates from dictionary.

        Args:
            data: The data in dictionary to be mapped 1:1

        Returns:
            The ProjectItem reconstructed from dict
        """

class Project(BaseModel):
    """GitHub Project V2 representation."""
    number: int
    title: str
    description: str | None
    resource_path: str | None
    closed: bool
    owner: str
    creator: str | None
    public: bool
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Project:
        """Create Project from dictionary.

        Args:
            data: Dictionary with project data

        Returns:
            Project instance
        """

class ProjectListMeta(BaseModel):
    """Metadata for project list response."""
    total_count: int
    start_cursor: str | None
    end_cursor: str | None
    error: str | None
