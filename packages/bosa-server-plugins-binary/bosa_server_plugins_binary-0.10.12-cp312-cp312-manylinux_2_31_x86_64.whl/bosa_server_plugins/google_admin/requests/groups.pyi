from bosa_server_plugins.handler import BaseRequestModel as BaseRequestModel

class ListGroupsRequest(BaseRequestModel):
    """List groups request model."""
    email: str
    cursor: str | None
