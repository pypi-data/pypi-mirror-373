from bosa_server_plugins.github.gql.fragments.issue_simple import GQLIssueSimple as GQLIssueSimple
from bosa_server_plugins.github.gql.fragments.pull_request_simple import GQLPullRequestSimple as GQLPullRequestSimple
from bosa_server_plugins.github.gql.fragments.repository import GQLRepository as GQLRepository
from bosa_server_plugins.github.gql.project_details import GQLProjectDetails as GQLProjectDetails
from typing import Any

class GQLPullRequest(GQLPullRequestSimple):
    """Pull request complete model."""
    closing_issues_references: list[GQLIssueSimple]
    repository: GQLRepository | None
    comments: int
    @classmethod
    def mapping(cls, data: dict) -> dict[str, Any]:
        """Create a GQLPullRequest mapping from a dictionary.

        Args:
            cls: GQLPullRequest class
            data: The dictionary to create the mapping from.

        Returns:
            GQLPullRequest: The created pull request.
        """

PULL_REQUEST_FRAGMENT: str
