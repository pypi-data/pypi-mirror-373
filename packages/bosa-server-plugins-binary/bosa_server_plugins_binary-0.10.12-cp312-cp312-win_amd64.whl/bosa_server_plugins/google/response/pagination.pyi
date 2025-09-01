from pydantic import BaseModel

class PaginationMeta(BaseModel):
    """Pagination metadata."""
    has_next: bool
    forwards_cursor: str
