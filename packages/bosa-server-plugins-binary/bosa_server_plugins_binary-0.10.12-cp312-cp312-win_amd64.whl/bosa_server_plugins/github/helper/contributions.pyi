from _typeshed import Incomplete
from bosa_server_plugins.auth.scheme import AuthenticationScheme as AuthenticationScheme
from bosa_server_plugins.cache import CacheService as CacheService
from bosa_server_plugins.github.gql.contributions import FragmentTypes as FragmentTypes, get_user_contributions as get_user_contributions
from bosa_server_plugins.github.helper.common import convert_to_datetime as convert_to_datetime, get_repository_objects as get_repository_objects
from bosa_server_plugins.github.helper.organization import get_organization_node_id_from_name as get_organization_node_id_from_name
from bosa_server_plugins.github.helper.repositories import get_organization_members as get_organization_members
from dataclasses import dataclass, field
from datetime import datetime
from github import Github
from github.Repository import Repository as Repository
from pydantic import BaseModel
from typing import Any, Generic, TypeVar

HTTP_NOT_FOUND: int
HTTP_CONFLICT: int
SIMILARITY_LOW_THRESHOLD: float
SIMILARITY_HIGH_THRESHOLD: float
SIMILARITY_USERNAME_THRESHOLD: float
MAX_MATCHES: int
MAX_COMMITS: int
UTC_TIMEZONE_SUFFIX: str
T = TypeVar('T', bound=BaseModel)

class UserCommitContribution(BaseModel):
    """Model for user repository contribution."""
    repository: str
    count: int

class UserIssueContribution(BaseModel):
    """Model for user issue contribution."""
    repository: str
    count: int
    count_open: int
    count_closed: int
    count_duplicated: int
    count_completed: int
    count_not_planned: int
    issue_numbers: list[int]

class UserPullRequestContribution(BaseModel):
    """Model for user pull request contribution."""
    repository: str
    count: int
    count_merged: int
    count_closed: int
    count_open: int
    pull_request_numbers: list[int]

class UserPullRequestReviewContribution(BaseModel):
    """Model for user pull request review contribution."""
    repository: str
    count: int
    comments: int
    approvals: int
    rejections: int
    dismissed_reviews: int
    pending_reviews: int
    pull_request_numbers: list[int]

class UserContributionAggregate(BaseModel, Generic[T]):
    """Model for user contribution."""
    total_contributions: int
    total_repositories: int
    breakdown: list[T]

class UserCommitContributionAggregate(UserContributionAggregate[UserCommitContribution]):
    """Model for user commit contribution."""

class UserIssueContributionAggregate(UserContributionAggregate[UserIssueContribution]):
    """Model for user issue contribution."""
    total_open_issues: int
    total_closed_issues: int
    total_duplicated_issues: int
    total_completed_issues: int
    total_not_planned_issues: int

class UserPullRequestContributionAggregate(UserContributionAggregate[UserPullRequestContribution]):
    """Model for user pull request contribution."""
    total_open_pull_requests: int
    total_closed_pull_requests: int
    total_merged_pull_requests: int

class UserPullRequestReviewContributionAggregate(UserContributionAggregate[UserPullRequestReviewContribution]):
    """Model for user pull request review contribution."""
    total_comments: int
    total_approvals: int
    total_rejections: int
    total_dismissed_reviews: int
    total_pending_reviews: int

class UserContributionStats(BaseModel):
    """New Model for contribution statistics."""
    commits_stats: UserCommitContributionAggregate | None
    prs_stats: UserPullRequestContributionAggregate | None
    issues_stats: UserIssueContributionAggregate | None
    pr_reviews_stats: UserPullRequestReviewContributionAggregate | None

class ContributionStats(BaseModel):
    """Model for contribution statistics.

    Note: Not used anymore (except in `search_contributions`). See UserContributionStats
    """
    username: str
    total_commits: int
    total_prs_created: int
    total_prs_merged: int
    total_issues_created: int
    repositories: list[str]
    period_start: datetime
    period_end: datetime
    total_repositories: int
    user_display_name: str | None

@dataclass
class ActivityContext:
    """Context for tracking GitHub user activity across repositories.

    Note: Not used anymore. See UserContributionStats
    """
    username: str
    since_date: datetime
    until_date: datetime
    activity_counts: dict[str, int] = field(default_factory=Incomplete)
    active_repos: set[str] = field(default_factory=set)
    def update_counts(self, activity_type: str, count: int, repo_name: str) -> None:
        """Update activity counts and active repositories."""
    def get_counts(self) -> dict[str, int]:
        """Return the current activity counts."""

def get_user_statistics(auth_scheme: AuthenticationScheme, cache_service: CacheService, *, since: str, until: str, statistics: list[FragmentTypes] | None = ..., organization: str | None, username: str | list[str] | None) -> dict[str, UserContributionStats]:
    """Get commit statistics for a user.

    Args:
        auth_scheme (AuthenticationScheme): Authentication scheme
        cache_service (CacheService): Cache service
        username (str | list[str] | None): GitHub username
        organization (str): GitHub organization
        since (str): Start date for contribution search
        until (str): End date for contribution search
        statistics (list[str]): List of statistics to retrieve

    Returns:
        UserContributionStats: Contribution statistics
    """
def search_contributors(auth_scheme: AuthenticationScheme, *, repositories: list[str] | None = None, name: str, since: str, until: str) -> Any:
    """Search contributors in specified repositories.

    Note: Use get_user_statistics instead.

    Args:
        auth_scheme (AuthenticationScheme): Authentication scheme
        repositories (Optional[List[str]], optional): List of repositories to search. Defaults to None.
        name (str): Name or username or email of the contributor to search.
        since (str): Start date for contributor search. Required `RFC 3339` string format.
        until (str): End date for contributor search. Required `RFC 3339` string format.

    Returns:
        Any: Search results and errors
    """
def get_user_activity_counts(github_client: Github, username: str, since: datetime, until: datetime, repositories: list[Repository] | None = None) -> dict[str, int]:
    """Get counts of different user activities based on a date range.

    Note: Use get_user_contributions instead.

    Args:
        github_client: GitHub client
        username: GitHub username
        since: Start date for filtering
        until: End date for filtering
        repositories: Optional list of repositories to check

    Returns:
        Dictionary with counts for different activity types
    """
