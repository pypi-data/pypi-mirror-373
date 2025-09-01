from dataclasses import dataclass
from typing import Any

@dataclass
class GithubAPIResponse:
    """Github API Response."""
    data: Any
    status_code: int
    pages: dict
    def __init__(self, data: Any, status_code: int = None, pages: dict | None = None) -> None:
        """Initialize the GithubAPIResponse.

        Args:
            data (Any): The response data.
            status_code (int): The HTTP status code. Defaults to None.
            pages (Optional[Dict]): The pagination information. Defaults to None.
        """
