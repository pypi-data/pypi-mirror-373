from pydantic import BaseModel

class CopyRequest(BaseModel):
    """Batch content document request model."""
    source_document_id: str
    start_index: int | None
    end_index: int | None
    destination_document_id: str
    destination_index: int
    add_ending_page_break: bool | None
