from bosa_server_plugins.github.gql.fragments.base import GQLBaseModel as GQLBaseModel
from typing import Any

class GQLLabel(GQLBaseModel):
    """Label model."""
    id: str
    name: str
    color: str
    description: str | None
    is_default: bool
    @classmethod
    def mapping(cls, data: dict) -> dict[str, Any]:
        """Create a GQLLabel mapping from a dictionary.

        Args:
            cls: GQLLabel class
            data: The dictionary to create the mapping from.

        Returns:
            GQLLabel: The created label.
        """

LABEL_FRAGMENT: str
