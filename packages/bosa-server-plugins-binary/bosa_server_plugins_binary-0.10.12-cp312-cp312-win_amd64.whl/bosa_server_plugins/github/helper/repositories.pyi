from .pagination import create_github_pagination_meta as create_github_pagination_meta
from _typeshed import Incomplete
from bosa_server_plugins.auth.scheme import AuthenticationScheme as AuthenticationScheme
from bosa_server_plugins.cache import CacheService as CacheService
from bosa_server_plugins.github.entities import Collaborator as Collaborator, Commit as Commit
from bosa_server_plugins.github.entities.release import Release as Release
from bosa_server_plugins.github.helper.connect import send_request_to_github as send_request_to_github
from enum import StrEnum
from typing import Any

MEMBERS_CACHE_TTL: Incomplete

class GithubCollaboratorAffiliation(StrEnum):
    """Github Collaborator Affiliation."""
    OUTSIDE = 'outside'
    DIRECT = 'direct'
    ALL = 'all'

class GithubCollaboratorPermission(StrEnum):
    """Github Collaborator Permissions."""
    PULL = 'pull'
    TRIAGE = 'triage'
    PUSH = 'push'
    MAINTAIN = 'maintain'
    ADMIN = 'admin'

def get_organization_members(auth_scheme: AuthenticationScheme, cache_service: CacheService, organization: str) -> tuple[list[str], Any]:
    """Get organization members.

    Args:
        auth_scheme: The authentication scheme.
        cache_service: The cache service.
        organization: The organization name.

    Returns:
        A tuple containing:
        - List[str]: The list of member logins.
        - Any: The pagination metadata.
    """
def get_repository_commits(owner: str, repo: str, auth_scheme: AuthenticationScheme, *, sha: str | None = None, path: str | None = None, author: str | None = None, since: str | None = None, until: str | None = None, per_page: int = 30, page: int = 1) -> tuple[list[Commit], Any]:
    """Get commits for a repository.

    Args:
        owner: The account owner of the repository
        repo: The name of the repository
        auth_scheme: The authentication scheme
        sha: SHA or branch to start listing commits from
        path: Only commits containing this file path will be returned
        author: GitHub login or email address by which to filter by commit author
        since: Only show results after this timestamp (ISO 8601 format)
        until: Only commits before this timestamp (ISO 8601 format)
        per_page: Results per page (max 100)
        page: Page number of the results to fetch

    Returns:
        A tuple containing:
        - List[Commit]: The list of commit objects.
        - Any: The pagination metadata.
    """
def get_repository_collaborators(owner: str, repo: str, auth_scheme: AuthenticationScheme, *, affiliation: GithubCollaboratorAffiliation | None = None, permission: GithubCollaboratorPermission | None = None, per_page: int = 30, page: int = 1) -> tuple[list[Collaborator], Any]:
    """Get collaborators for a repository.

    Args:
        owner: The account owner of the repository
        repo: The name of the repository
        auth_scheme: The authentication scheme
        affiliation: Filter collaborators by their affiliation
        permission: Filter collaborators by their permission level
        per_page: Results per page (max 100)
        page: Page number of the results to fetch

    Returns:
        A tuple containing:
        - List[Collaborator]: The list of collaborator objects.
        - Any: The pagination metadata.
    """
def get_repository_releases(owner: str, repo: str, auth_scheme: AuthenticationScheme, per_page: int | None = 30, page: int | None = 1) -> list[Release]:
    """Get releases for a repository.

    Args:
        owner: The account owner of the repository
        repo: The name of the repository
        auth_scheme: The authentication scheme
        per_page: Results per page (max 100)
        page: Page number of the results to fetch

    Returns:
        List of Release objects containing release information
    """
def get_repository_languages(owner: str, repo: str, auth_scheme: AuthenticationScheme) -> dict:
    """Get languages for a repository.

    Args:
        owner: The account owner of the repository
        repo: The name of the repository
        auth_scheme: The authentication scheme

    Returns:
        Dictionary containing language information
    """
