from pydantic import BaseModel
from typing import Any, Literal

class Oauth2AuthorizationRequest(BaseModel):
    """Request model for authorization callback."""
    auth_type: Literal['oauth2']
    callback_url: str
    @classmethod
    def set_default_auth_type(cls, data: Any) -> Any:
        """Set auth_type to oauth2 if missing for backwards compatibility."""

class CustomConfigurationRequest(BaseModel):
    """Request model for custom configuration callback."""
    auth_type: Literal['custom']
    configuration: dict[str, Any]
AuthorizationRequest = Oauth2AuthorizationRequest | CustomConfigurationRequest
