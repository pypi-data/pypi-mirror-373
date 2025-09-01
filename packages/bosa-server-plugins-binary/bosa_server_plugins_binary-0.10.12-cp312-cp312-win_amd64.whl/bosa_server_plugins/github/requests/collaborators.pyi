from bosa_server_plugins.github.helper.repositories import GithubCollaboratorAffiliation as GithubCollaboratorAffiliation, GithubCollaboratorPermission as GithubCollaboratorPermission
from bosa_server_plugins.github.requests.repositories import BasicRepositoryRequest as BasicRepositoryRequest

class GetCollaboratorsRequest(BasicRepositoryRequest):
    """Request model for getting repository collaborators.

    This model is based on the GitHub REST API for listing repository collaborators.
    """
    affiliation: GithubCollaboratorAffiliation | None
    permission: GithubCollaboratorPermission | None
    per_page: int | None
    page: int | None
