from bosa_server_plugins.github.gql.fragments.base import GQLBaseModel as GQLBaseModel
from bosa_server_plugins.github.gql.fragments.label import GQLLabel as GQLLabel
from bosa_server_plugins.github.gql.project_details import GQLProjectDetails as GQLProjectDetails
from datetime import datetime
from typing import Any

class GQLPullRequestSimple(GQLBaseModel):
    """Pull request model."""
    assignees: list[str] | None
    author: str | None
    body: str
    body_html: str
    body_text: str
    closed: bool
    draft: bool | None
    closed_at: datetime | None
    created_at: datetime
    updated_at: datetime
    merged_at: datetime | None
    number: int
    title: str
    url: str
    state: str
    labels: list[GQLLabel] | None
    project_details: GQLProjectDetails | None
    @classmethod
    def mapping(cls, data: dict) -> dict[str, Any]:
        """Create a GQLPullRequestSimple mapping from a dictionary.

        Args:
            cls: GQLPullRequestSimple class
            data: The dictionary to create the mapping from.

        Returns:
            GQLPullRequestSimple: The created pull request.
        """

PULL_REQUEST_SIMPLE_FRAGMENT: str
