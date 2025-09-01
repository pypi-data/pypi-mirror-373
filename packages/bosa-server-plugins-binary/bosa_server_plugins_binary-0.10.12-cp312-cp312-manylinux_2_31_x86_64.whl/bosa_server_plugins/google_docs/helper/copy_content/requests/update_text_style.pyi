from _typeshed import Incomplete
from bosa_server_plugins.google_docs.helper.copy_content.requests.base import BatchUpdateRequest as BatchUpdateRequest

class UpdateTextStyle(BatchUpdateRequest):
    """Google Docs update text style batch update request."""
    style: Incomplete
    style_length: Incomplete
    def __init__(self, style: dict, style_length: int = 1) -> None:
        """Initialize the UpdateTextStyle object.

        Args:
            style: The style of the text.
            style_length: The length of the text style.
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
