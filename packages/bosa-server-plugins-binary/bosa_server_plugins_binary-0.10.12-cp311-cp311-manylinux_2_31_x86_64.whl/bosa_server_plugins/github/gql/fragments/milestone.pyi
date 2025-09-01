from bosa_server_plugins.github.gql.fragments.base import GQLBaseModel as GQLBaseModel
from datetime import datetime
from typing import Any

class GQLMilestone(GQLBaseModel):
    """Milestone model."""
    id: str
    number: int
    title: str
    description: str
    closed: bool
    state: str
    created_at: datetime | None
    updated_at: datetime | None
    closed_at: datetime | None
    due_on: datetime | None
    @classmethod
    def mapping(cls, data: dict) -> dict[str, Any]:
        """Create a GQLMilestone mapping from a dictionary.

        Args:
            cls: GQLMilestone class
            data: The dictionary to create the mapping from.

        Returns:
            GQLMilestone: The created milestone.
        """

MILESTONE_FRAGMENT: str
