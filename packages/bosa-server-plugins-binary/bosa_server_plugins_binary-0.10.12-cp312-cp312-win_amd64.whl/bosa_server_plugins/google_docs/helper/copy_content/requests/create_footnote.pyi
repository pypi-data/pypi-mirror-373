from _typeshed import Incomplete
from bosa_server_plugins.google_docs.helper.copy_content.requests.base import BatchUpdateRequest as BatchUpdateRequest, DEFAULT_ELEMENT_LENGTH as DEFAULT_ELEMENT_LENGTH
from bosa_server_plugins.google_docs.helper.copy_content.requests.structural_element.base import StructuralElement as StructuralElement

class CreateFootnote(BatchUpdateRequest):
    """Google Docs create footnote batch update request."""
    contents: Incomplete
    def __init__(self, contents: list[StructuralElement]) -> None:
        """Initialize the CreateFootnote request.

        Args:
            contents: The contents of the footnote.
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
