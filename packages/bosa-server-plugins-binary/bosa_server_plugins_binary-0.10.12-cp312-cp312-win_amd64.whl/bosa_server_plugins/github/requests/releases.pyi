from bosa_server_plugins.github.requests.repositories import BasicRepositoryRequest as BasicRepositoryRequest

class GetReleasesRequest(BasicRepositoryRequest):
    """Request model for getting repository releases."""
    per_page: int | None
    page: int | None
