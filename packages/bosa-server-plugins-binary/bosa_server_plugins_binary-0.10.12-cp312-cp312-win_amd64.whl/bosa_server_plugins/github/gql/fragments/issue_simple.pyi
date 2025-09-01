from bosa_server_plugins.github.gql.fragments.base import GQLBaseModel as GQLBaseModel
from bosa_server_plugins.github.gql.project_details import GQLProjectDetails as GQLProjectDetails
from typing import Any

class GQLIssueSimple(GQLBaseModel):
    """Issue simple model."""
    id: str
    title: str
    parent_number: int | None
    parent_url: str | None
    project_details: GQLProjectDetails | None
    @classmethod
    def mapping(cls, data: dict) -> dict[str, Any]:
        """Create a GQLIssueSimple mapping from a dictionary.

        Args:
            cls: GQLIssueSimple class
            data: The dictionary to create the mapping from.

        Returns:
            Dict[str, Any]: The created mapping.
        """

ISSUE_SIMPLE_FRAGMENT: str
