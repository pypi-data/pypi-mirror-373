from pydantic import BaseModel

class DownloadFileRequest(BaseModel):
    """Download file request model."""
    id: str
    export_format: str | None
    revision_id: str | None
    acknowledge_abuse: bool | None
    supports_all_drives: bool | None
