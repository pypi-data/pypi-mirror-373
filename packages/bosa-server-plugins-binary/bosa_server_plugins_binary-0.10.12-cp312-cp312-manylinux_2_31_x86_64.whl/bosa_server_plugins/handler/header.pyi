from pydantic import BaseModel

class HttpHeaders:
    """HTTP Headers."""
    def __init__(self, headers: dict[str, str]) -> None:
        """Constructor.

        Args:
            headers (dict[str, str]): The headers
        """
    @property
    def authorization(self) -> str | None:
        """Get the Authorization header.

        Returns:
            str | None: The Authorization header value
        """
    @property
    def content_type(self) -> str | None:
        """Get the Content-Type header.

        Returns:
            str | None: The Content-Type header value
        """
    @property
    def accept(self) -> str | None:
        """Get the Accept header.

        Returns:
            str | None: The Accept header value
        """
    def get_header(self, name: str) -> str | None:
        """Get a header by name.

        Args:
            name (str): The header name

        Returns:
            str | None: The header value
        """

class ExposedDefaultHeaders(BaseModel):
    """Exposed default headers."""
    x_api_key: str
    authorization: str | None
    x_bosa_integration: str | None
    content_type: str | None
    accept: str | None
    user_agent: str | None
    x_forwarded_for: str | None
    x_forwarded_proto: str | None
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed: bool
