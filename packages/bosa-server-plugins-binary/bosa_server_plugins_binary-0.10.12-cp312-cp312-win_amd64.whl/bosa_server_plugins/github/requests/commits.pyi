from bosa_server_plugins.github.requests.common import validate_fields_datetime_iso_8601 as validate_fields_datetime_iso_8601
from bosa_server_plugins.github.requests.repositories import BasicRepositoryRequest as BasicRepositoryRequest
from bosa_server_plugins.github.tasks.get_all_pr_commits_task import CommitFields as CommitFields
from bosa_server_plugins.handler.model import BaseRequestModel as BaseRequestModel

class GetCommitsRequest(BasicRepositoryRequest):
    """Request model for listing repository commits, based on the GitHub REST API."""
    sha: str | None
    path: str | None
    author: str | None
    committer: str | None
    per_page: int | None
    page: int | None
    since: str | None
    until: str | None
    def validate_dates(self):
        """Validate date format."""

class SearchCommitsRequest(BaseRequestModel):
    """Request model for searching repository commits."""
    repositories: list[str] | None
    author: str | None
    fields: list[CommitFields] | None
    summarize: bool | None
    callback_urls: list[str] | None
    since: str | None
    until: str | None
    def validate_dates(self):
        """Validate date format."""
