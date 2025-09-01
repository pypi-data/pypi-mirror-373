from pydantic import BaseModel

class GithubApiCursorMeta(BaseModel):
    """Github API Cursor Meta."""
    total: int
    total_page: int
    has_next: bool
    has_prev: bool
    backwards_cursor: str | None
    forwards_cursor: str | None
