from bosa_server_plugins.github.gql.fragments.base import GQLBaseModel as GQLBaseModel
from bosa_server_plugins.github.gql.project_details import GQLProjectDetails as GQLProjectDetails
from typing import Any

class GQLIssueProjectDetails(GQLBaseModel):
    """Issue model."""
    number: int
    project_details: GQLProjectDetails | None
    @classmethod
    def mapping(cls, data: dict) -> dict[str, Any]:
        """Create a GQLIssue mapping from a dictionary.

        Args:
            cls: GQLIssue class
            data: The dictionary to create the mapping from.

        Returns:
            Dict[str, Any]: The created mapping.
        """

ISSUE_PROJECT_DETAILS_FRAGMENT: str
