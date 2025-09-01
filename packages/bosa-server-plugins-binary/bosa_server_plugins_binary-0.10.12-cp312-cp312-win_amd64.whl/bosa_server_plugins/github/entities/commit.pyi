from bosa_server_plugins.cache import CacheService as CacheService
from bosa_server_plugins.github.constant import GITHUB_DATE_FORMAT as GITHUB_DATE_FORMAT, GITHUB_PR_COMMITS_CACHE_KEY as GITHUB_PR_COMMITS_CACHE_KEY
from bosa_server_plugins.github.entities.user import GitUser as GitUser, SimpleUser as SimpleUser
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from github import Github as Github, Repository as Repository
from typing import Any, NamedTuple

class FileStatus(str, Enum):
    """File Statuses."""
    ADDED = 'added'
    REMOVED = 'removed'
    MODIFIED = 'modified'
    RENAMED = 'renamed'
    COPIED = 'copied'
    CHANGED = 'changed'
    UNCHANGED = 'unchanged'

@dataclass
class TreeInfo:
    """Tree Info."""
    sha: str
    url: str

@dataclass
class Verification:
    """Represents verification information for a commit."""
    verified: bool
    reason: str
    signature: str | None = ...
    payload: str | None = ...
    verified_at: datetime | None = ...

@dataclass
class CommitDetails:
    """Commit Details."""
    url: str
    message: str
    tree: TreeInfo
    comment_count: int
    verification: Verification
    author: GitUser | None = ...
    committer: GitUser | None = ...

@dataclass
class CommitParent:
    """Commit Parent."""
    sha: str
    url: str
    html_url: str | None = ...

@dataclass
class CommitStats:
    """Commit stats."""
    additions: int
    deletions: int
    total: int

@dataclass
class DiffEntry:
    """Represents a file change in a commit."""
    sha: str
    filename: str
    status: FileStatus
    additions: int
    deletions: int
    changes: int
    blob_url: str
    raw_url: str
    contents_url: str
    patch: str | None = ...
    previous_filename: str | None = ...

@dataclass
class Commit:
    """Represents a GitHub commit."""
    url: str
    sha: str
    node_id: str
    html_url: str
    comments_url: str
    commit: CommitDetails
    parents: list[CommitParent]
    author: SimpleUser | None = ...
    committer: SimpleUser | None = ...
    stats: CommitStats | None = ...
    files: list[DiffEntry] | None = ...
    @classmethod
    def from_dict(cls, data: dict) -> Commit:
        """Create a Commit instance from a dictionary.

        Args:
            data: Dictionary containing commit data from GitHub API

        Returns:
            Commit instance
        """

@dataclass
class SearchFilters:
    """Search filters for commit search operations.

    Contains all filter parameters for searching commits:
    - author: GitHub username to filter commits by
    - since_date: Start date for commit search
    - until_date: End date for commit search
    - fields: List of fields to extract from commits

    Attributes:
        author (Optional[str]): GitHub username to filter commits by.
        since_date (Optional[datetime]): Start date for commit search.
        until_date (Optional[datetime]): End date for commit search.
        fields (Optional[List[str]]): List of fields to extract from commits.
    """
    author: str | None = ...
    since_date: datetime | None = ...
    until_date: datetime | None = ...
    fields: list[str] | None = ...

@dataclass
class CommitSearchContext:
    """Context object for commit search operations.

    Holds the search parameters and results for a commit search operation.
    Provides caching functionality through the cache_key property.

    Attributes:
        repository (str): Repository name in format 'org/repo'.
        filters (SearchFilters): Search filters containing author, date range, and field filters.
        processed_commits (List[Dict[str, Any]]): List of processed commits with their details.
        commit_sha_set (Set[str]): Set of processed commit SHAs to avoid duplicates.
        is_processing (bool): Flag indicating if commit processing is in progress.
    """
    repository: str
    filters: SearchFilters = field(default_factory=SearchFilters)
    processed_commits: list[dict[str, Any]] = field(default_factory=list)
    commit_sha_set: set[str] = field(default_factory=set)
    is_processing: bool = ...
    @property
    def cache_key(self) -> str:
        """Generate cache key based on search parameters.

        The key is constructed from repository name, author, and date range filters.

        Returns:
            str: A unique cache key string based on the search parameters.
        """

class PRCommitConfig(NamedTuple):
    """Configuration for PR commit retrieval.

    Contains all necessary parameters for retrieving commits from pull requests.

    Attributes:
        github_client (Github): Authenticated GitHub client.
        repo (Repository): GitHub repository object.
        repository (str): Repository name in format 'org/repo'.
        context (Optional[CommitSearchContext]): Optional search context containing filters and results.
        background_tasks (Optional[BackgroundTasks]): FastAPI background tasks for async processing.
        cache_service (Optional[CacheService]): Cache service for storing results.
    """
    github_client: Github
    repo: Repository
    repository: str
    context: CommitSearchContext | None
    cache_service: CacheService
