from bosa_server_plugins.github.gql.fragments.base import GQLBaseModel as GQLBaseModel
from bosa_server_plugins.github.gql.fragments.label import GQLLabel as GQLLabel
from bosa_server_plugins.github.gql.fragments.milestone import GQLMilestone as GQLMilestone
from bosa_server_plugins.github.gql.fragments.pull_request_simple import GQLPullRequestSimple as GQLPullRequestSimple
from bosa_server_plugins.github.gql.fragments.repository import GQLRepository as GQLRepository
from bosa_server_plugins.github.gql.project_details import GQLProjectDetails as GQLProjectDetails
from datetime import datetime
from typing import Any

class GQLIssue(GQLBaseModel):
    """Issue model."""
    id: str
    assignees: list[str] | None
    number: int
    body: str
    state: str
    closed_at: datetime | None
    closed_by: list[GQLPullRequestSimple] | None
    labels: list[GQLLabel] | None
    milestone: GQLMilestone | None
    project_details: GQLProjectDetails | None
    author: str | None
    created_at: datetime
    updated_at: datetime
    title: str
    url: str
    parent_number: int | None
    parent_url: str | None
    repository: GQLRepository | None
    comments: int
    @classmethod
    def mapping(cls, data: dict) -> dict[str, Any]:
        """Create a GQLIssue mapping from a dictionary.

        Args:
            cls: GQLIssue class
            data: The dictionary to create the mapping from.

        Returns:
            Dict[str, Any]: The created mapping.
        """

ISSUE_FRAGMENT: str
