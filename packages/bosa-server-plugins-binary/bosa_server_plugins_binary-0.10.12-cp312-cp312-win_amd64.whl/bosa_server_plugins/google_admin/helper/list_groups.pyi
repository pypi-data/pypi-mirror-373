from bosa_server_plugins.google_admin.requests.groups import ListGroupsRequest as ListGroupsRequest
from bosa_server_plugins.google_admin.services.groups import GoogleAdminGroupsService as GoogleAdminGroupsService
from typing import Any

MAX_RESULTS: int

def list_groups(request: ListGroupsRequest, groups_service: GoogleAdminGroupsService) -> dict[str, Any]:
    """List groups in a Google Admin SDK.

    This function serves as a wrapper for the Google Admin SDK API directory_v1 groups().list() method.

    Args:
        request: The ListGroupsRequest object containing request details
        groups_service: The Google Admin groups service

    Returns:
        The list of groups
    """
