from _typeshed import Incomplete
from bosa_server_plugins.google_docs.helper.copy_content.requests.base import BatchUpdateRequest as BatchUpdateRequest, DEFAULT_ELEMENT_LENGTH as DEFAULT_ELEMENT_LENGTH

class InsertTable(BatchUpdateRequest):
    """Google Docs insert table batch update request."""
    rows: Incomplete
    columns: Incomplete
    def __init__(self, rows: int, columns: int) -> None:
        """Initialize the InsertTable object.

        Args:
            rows: The number of rows in the table.
            columns: The number of columns in the table.
        """
    def length(self) -> int:
        """Length of the content.

        Used to update the cursor position after pasting.

        Returns:
            int: The length of the content that was pasted.
        """
    def paste(self, index: int, segment_id: str = None) -> dict:
        """Generate the batch update request for pasting the content in specified index and segment.

        Args:
            index: The index where the content will be pasted.
            segment_id: The segment ID for the content.

        Returns:
            A dictionary representing the batch update request.
        """
