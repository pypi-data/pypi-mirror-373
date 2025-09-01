from bosa_server_plugins.github.helper.projects import CustomFieldFilter as CustomFieldFilter
from bosa_server_plugins.github.requests.common import GithubCursorListRequest as GithubCursorListRequest, validate_fields_datetime_iso_8601 as validate_fields_datetime_iso_8601
from bosa_server_plugins.handler import BaseRequestModel as BaseRequestModel
from enum import Enum

class PermissionLevel(str, Enum):
    """Permission levels for GitHub projects."""
    ADMIN = 'ADMIN'
    READ = 'READ'
    WRITE = 'WRITE'

class OrderByDirection(str, Enum):
    """Order by direction."""
    ASC = 'ASC'
    DESC = 'DESC'

class OrderByField(str, Enum):
    """Order by field."""
    CREATED_AT = 'CREATED_AT'
    NUMBER = 'NUMBER'
    TITLE = 'TITLE'
    UPDATED_AT = 'UPDATED_AT'

class GithubProjectBaseRequest(BaseRequestModel):
    """Github Projects V2 Base Request."""
    organization: str
    number: int
    per_page: int | None
    page: int | None
    force_new: bool | None

class GithubListProjectCardsRequest(GithubProjectBaseRequest):
    """Github List Project Cards Request Body."""
    status: str | None
    type: str | None
    created_at_from: str | None
    created_at_to: str | None
    updated_at_from: str | None
    updated_at_to: str | None
    filters: list[CustomFieldFilter] | None
    summarize: bool | None
    def validate_dates(self) -> GithubListProjectCardsRequest:
        """Validate that all date fields are in the correct ISO 8601 format."""

class GithubListProjectBaseRequest(BaseRequestModel):
    """Github List Project Base Request."""
    organization: str
    query: str | None
    min_permission_level: PermissionLevel | None

class GithubListProjectsRequest(GithubCursorListRequest, GithubListProjectBaseRequest):
    """Github List Projects Request Body."""
    order_by: OrderByField | None
    direction: OrderByDirection | None
