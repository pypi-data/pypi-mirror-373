from bosa_server_plugins.handler import BaseRequestModel as BaseRequestModel
from datetime import datetime

class BaseCommentsRequestModel(BaseRequestModel):
    """Base request model for Google Docs comments."""
    document_id: str

class ListCommentsRequest(BaseCommentsRequestModel):
    """List comment request model."""
    page_size: int | None
    page_token: str | None
    include_deleted: bool | None
    start_modified_time: str | None
    end_modified_time: str | None
    def validate_dates(self):
        """Validate date format."""

class SummarizeCommentsRequest(BaseCommentsRequestModel):
    """Summarize comments request model."""

def validate_date_format(date: str | None) -> datetime | None:
    """Validate date format.

    Args:
        date (Optional[str]): The date to validate.

    Returns:
        Optional[datetime]: The validated date.

    Raises:
        ValueError: If the date is not in RFC 3339 format.
    """
