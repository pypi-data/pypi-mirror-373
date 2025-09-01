from bosa_server_plugins.github.gql.fragments.base import GQLBaseModel as GQLBaseModel
from typing import Any

class GQLRepository(GQLBaseModel):
    """Repository model."""
    name: str
    owner: str
    @classmethod
    def mapping(cls, data: dict) -> dict[str, Any]:
        """Create a GQLRepository mapping from a dictionary.

        Args:
            cls: GQLRepository class
            data: The dictionary to create the mapping from.

        Returns:
            Dict[str, Any]: The created mapping.
        """

REPOSITORY_FRAGMENT: str
