from _typeshed import Incomplete
from bosa_server_plugins.google_docs.helper.copy_content.requests.base import BatchUpdateRequest as BatchUpdateRequest

class CreateParagraphBullet(BatchUpdateRequest):
    """Google Docs create paragraph bullet batch update request."""
    content_length: Incomplete
    bullet_preset: Incomplete
    def __init__(self, length: int, bullet_preset: str = 'BULLET_DISC_CIRCLE_SQUARE') -> None:
        """Initialize the CreateParagraphBullet object.

        Args:
            length: The length of the content.
            bullet_preset: The bullet preset for the paragraph.
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
