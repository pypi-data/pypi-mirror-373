from bosa_server_plugins.github.gql.project import GQLProjectBasic as GQLProjectBasic, GQLProjectItemBasic as GQLProjectItemBasic
from pydantic import BaseModel

class GQLProjectDetails(BaseModel):
    """Container for project-related data that can be used by GitHub entities."""
    project_items: list[GQLProjectItemBasic]
    projects: list[GQLProjectBasic]
    @classmethod
    def from_dict(cls, data: dict) -> GQLProjectDetails:
        """Parse project items and projects from GraphQL response data.

        Args:
            data: The GraphQL response data

        Returns:
            GQLProjectDetails: Object containing parsed project data
        """
