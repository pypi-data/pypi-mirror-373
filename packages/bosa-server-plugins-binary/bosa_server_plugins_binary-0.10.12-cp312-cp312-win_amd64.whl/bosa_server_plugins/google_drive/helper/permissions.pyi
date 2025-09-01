from bosa_server_plugins.common.email import extract_domain_from_an_email_address as extract_domain_from_an_email_address
from bosa_server_plugins.google_drive.requests.permissions import CreatePermissionRequest as CreatePermissionRequest, DeletePermissionRequest as DeletePermissionRequest, GetPermissionRequest as GetPermissionRequest, ListPermissionRequest as ListPermissionRequest, TypeEnum as TypeEnum, UpdatePermissionRequest as UpdatePermissionRequest
from bosa_server_plugins.google_drive.services.files import GoogleDriveFileService as GoogleDriveFileService
from bosa_server_plugins.google_drive.services.permissions import GoogleDrivePermissionsService as GoogleDrivePermissionsService

def create_permission(request: CreatePermissionRequest, permission_service: GoogleDrivePermissionsService, file_service: GoogleDriveFileService):
    """Create a permission for a file or folder in Google Drive.

    Args:
        request: The request object
        permission_service: GoogleDrivePermissionsService instance
        file_service: GoogleDriveFileService instance
    """
def list_permissions(request: ListPermissionRequest, service: GoogleDrivePermissionsService):
    """List permissions for a file or folder in Google Drive.

    Args:
        request: The request object
        service: GoogleDrivePermissionsService instance
    """
def get_permission(request: GetPermissionRequest, service: GoogleDrivePermissionsService):
    """Get a specific permission for a file or folder in Google Drive.

    Args:
        request: The request object
        service: GoogleDrivePermissionsService instance
    """
def update_permission(request: UpdatePermissionRequest, service: GoogleDrivePermissionsService):
    """Update a permission for a file or folder in Google Drive.

    Args:
        request: The request object
        service: GoogleDrivePermissionsService instance
    """
def delete_permission(request: DeletePermissionRequest, service: GoogleDrivePermissionsService):
    """Delete a permission from a file or folder in Google Drive.

    Args:
        request: The request object
        service: GoogleDrivePermissionsService instance
    """
