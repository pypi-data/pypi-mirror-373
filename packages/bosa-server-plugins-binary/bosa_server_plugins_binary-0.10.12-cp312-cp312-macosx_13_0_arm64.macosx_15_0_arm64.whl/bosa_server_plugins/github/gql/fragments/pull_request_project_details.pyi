from bosa_server_plugins.github.gql.fragments.base import GQLBaseModel as GQLBaseModel
from bosa_server_plugins.github.gql.project_details import GQLProjectDetails as GQLProjectDetails
from typing import Any

class GQLPullRequestProjectDetails(GQLBaseModel):
    """Pull Request model with project details (for testing)."""
    number: int
    project_details: GQLProjectDetails | None
    @classmethod
    def mapping(cls, data: dict) -> dict[str, Any]:
        """Create a GQLPullRequestProjectDetails mapping from a dictionary.

        Args:
            cls: GQLPullRequestProjectDetails class
            data: The dictionary to create the mapping from.

        Returns:
            Dict[str, Any]: The created mapping.
        """

PULL_REQUEST_PROJECT_DETAILS_FRAGMENT: str
