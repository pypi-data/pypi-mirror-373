from _typeshed import Incomplete
from bosa_server_plugins.google_docs.helper.copy_content.requests.base import BatchUpdateRequest as BatchUpdateRequest, DEFAULT_ELEMENT_LENGTH as DEFAULT_ELEMENT_LENGTH

class InsertInlineImage(BatchUpdateRequest):
    """Google Docs insert inline image batch update request."""
    image_uri: Incomplete
    size: Incomplete
    def __init__(self, image_uri: str, size: dict) -> None:
        """Initialize the InsertInlineImage object.

        Args:
            image_uri: The URI of the image to be inserted.
            size: The size of the image.
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
