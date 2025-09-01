from bosa_server_plugins.google_docs.requests.comments import validate_date_format as validate_date_format
from bosa_server_plugins.handler import BaseRequestModel as BaseRequestModel
from enum import StrEnum
from pydantic import BaseModel

class BasePermissionRequest:
    """Base class for permission requests."""
    file_id: str
    supports_all_drives: bool | None
    use_domain_admin_access: bool | None

class RoleEnum(StrEnum):
    """Enum for permission roles."""
    READER = 'reader'
    COMMENTER = 'commenter'
    WRITER = 'writer'
    FILE_ORGANIZER = 'fileOrganizer'
    ORGANIZER = 'organizer'
    OWNER = 'owner'

class TypeEnum(StrEnum):
    """Enum for permission types."""
    USER = 'user'
    GROUP = 'group'
    DOMAIN = 'domain'
    ANYONE = 'anyone'

class CreatePermissionRequest(BasePermissionRequest, BaseRequestModel):
    """Create permission request model."""
    role: RoleEnum
    type: TypeEnum
    email_address: str | None
    expiration_time: str | None
    allow_file_discovery: bool | None
    view: str | None
    email_message: str | None
    move_to_new_owners_root: bool | None
    send_notification_email: bool | None
    transfer_ownership: bool | None
    def validate_dates(self):
        """Validate date format."""

class ListPermissionRequest(BasePermissionRequest, BaseRequestModel):
    """List permission request model."""
    include_permissions_for_view: str | None
    page_size: int | None
    page_token: str | None

class GetPermissionRequest(BasePermissionRequest, BaseRequestModel):
    """Get permission request model."""
    permission_id: str

class UpdatePermissionRequest(BasePermissionRequest, BaseRequestModel):
    """Update permission request model."""
    permission_id: str
    role: RoleEnum | None
    expiration_time: str | None
    remove_expiration: bool | None
    transfer_ownership: bool | None
    enforce_expensive_access: bool | None
    def validate_dates(self):
        """Validate date format."""

class DeletePermissionRequest(BasePermissionRequest, BaseModel):
    """Delete permission request model."""
    file_id: str
    permission_id: str
    enforce_expensive_access: bool | None
