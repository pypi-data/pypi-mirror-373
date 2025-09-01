from _typeshed import Incomplete
from bosa_server_plugins.google_docs.helper.copy_content.requests.base import BatchUpdateRequest as BatchUpdateRequest

MAXIMUM_NON_SURROGATE_VALUE: int

class InsertText(BatchUpdateRequest):
    """Google Docs insert text batch update request."""
    text: Incomplete
    def __init__(self, text: str) -> None:
        """Initialize the InsertText object.

        Args:
            text: The text content.
        """
    def length(self) -> int:
        """Length of the content.

        Used to update the cursor position after pasting.

        Returns:
            int: The length of the content that was pasted.
        """
    def get_utf16_surrogate_pairs(self):
        """Get total of surrogate pairs in the text."""
    def paste(self, index: int, segment_id: str = None) -> dict:
        """Generate the batch update request for pasting the content in specified index and segment.

        Args:
            index: The index where the content will be pasted.
            segment_id: The segment ID for the content.

        Returns:
            A dictionary representing the batch update request.
        """
