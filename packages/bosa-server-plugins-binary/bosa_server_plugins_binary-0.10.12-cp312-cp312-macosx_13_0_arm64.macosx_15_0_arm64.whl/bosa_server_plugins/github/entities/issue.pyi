from bosa_server_plugins.github.entities.user import SimpleUser as SimpleUser
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Label:
    """A GitHub issue label."""
    id: int
    node_id: str
    url: str
    name: str
    color: str
    default: bool
    description: str | None = ...
    @classmethod
    def from_dict(cls, data: dict) -> Label:
        """Create a Label instance from a dictionary."""

@dataclass
class PullRequest:
    """A GitHub pull request reference."""
    url: str
    html_url: str
    diff_url: str
    patch_url: str
    @classmethod
    def from_dict(cls, data: dict) -> PullRequest:
        """Create a PullRequest instance from a dictionary."""

@dataclass
class Milestone:
    """A GitHub milestone."""
    id: int
    node_id: str
    number: int
    state: str
    title: str
    open_issues: int
    closed_issues: int
    created_at: datetime
    updated_at: datetime
    url: str
    html_url: str
    labels_url: str
    description: str | None = ...
    creator: SimpleUser | None = ...
    closed_at: datetime | None = ...
    due_on: datetime | None = ...
    @classmethod
    def from_dict(cls, data: dict) -> Milestone:
        """Create a Milestone instance from a dictionary."""

@dataclass
class LicenseSimple:
    """License simple entity."""
    key: str
    name: str
    node_id: str
    url: str | None = ...
    spdx_id: str | None = ...
    html_url: str | None = ...

@dataclass
class Repository:
    """Repository entity."""
    id: int
    node_id: str
    name: str
    full_name: str
    owner: SimpleUser
    private: bool
    html_url: str
    fork: bool
    url: str
    archive_url: str
    assignees_url: str
    blobs_url: str
    branches_url: str
    collaborators_url: str
    comments_url: str
    commits_url: str
    compare_url: str
    contents_url: str
    contributors_url: str
    deployments_url: str
    downloads_url: str
    events_url: str
    forks: int
    description: str | None = ...
    license: LicenseSimple | None = ...
    permissions: dict | None = ...

@dataclass
class Issue:
    """Issue."""
    id: int
    node_id: str
    number: int
    state: str
    title: str
    locked: bool
    comments: int
    created_at: datetime
    updated_at: datetime
    author_association: str
    url: str
    repository_url: str
    labels_url: str
    comments_url: str
    events_url: str
    html_url: str
    labels: list[Label]
    body: str | None = ...
    user: SimpleUser | None = ...
    assignee: SimpleUser | None = ...
    assignees: list[SimpleUser] | None = ...
    milestone: Milestone | None = ...
    active_lock_reason: str | None = ...
    pull_request: PullRequest | None = ...
    closed_at: datetime | None = ...
    closed_by: SimpleUser | None = ...
    state_reason: str | None = ...
    body_html: str | None = ...
    body_text: str | None = ...
    timeline_url: str | None = ...
    repository: Repository | None = ...
    draft: bool | None = ...
    @classmethod
    def from_dict(cls, data: dict) -> Issue:
        """Create an Issue instance from a dictionary.

        Args:
            data: Dictionary containing issue data from GitHub API

        Returns:
            Issue instance
        """
