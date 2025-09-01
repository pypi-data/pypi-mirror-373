from bosa_server_plugins.github.entities.user import SimpleUser as SimpleUser
from dataclasses import dataclass

@dataclass
class ContributorWeek:
    """A week of contributor activity."""
    w: int
    a: int
    d: int
    c: int
    @classmethod
    def from_dict(cls, data: dict) -> ContributorWeek:
        """Create a ContributorWeek instance from a dictionary.

        Args:
            data: Dictionary containing contributor week data from GitHub API

        Returns:
            ContributorWeek instance
        """

@dataclass
class Contributor:
    """A GitHub repository contributor with activity statistics."""
    author: SimpleUser | None
    total: int
    weeks: list[ContributorWeek]
    @classmethod
    def from_dict(cls, data: dict) -> Contributor:
        """Create a Contributor instance from a dictionary.

        Args:
            data: Dictionary containing contributor data from GitHub API

        Returns:
            Contributor instance
        """
