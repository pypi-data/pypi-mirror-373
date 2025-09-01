from _typeshed import Incomplete
from bosa_server_plugins.google_docs.helper.copy_content.requests.create_footnote import CreateFootnote as CreateFootnote
from bosa_server_plugins.google_docs.helper.copy_content.requests.paragraph_element.paragraph_element import ParagraphElement as ParagraphElement
from bosa_server_plugins.google_docs.helper.copy_content.requests.structural_element.base import StructuralElement as StructuralElement
from bosa_server_plugins.google_docs.helper.copy_content.requests.update_paragraph_style import UpdateParagraphStyle as UpdateParagraphStyle

class Paragraph(StructuralElement):
    """Google Docs paragraph batch update request."""
    elements: Incomplete
    style: Incomplete
    def __init__(self, elements: list[ParagraphElement], style: dict) -> None:
        """Initialize the Paragraph object.

        Args:
            elements: The elements in the paragraph.
            style: The style of the paragraph.
        """
    def prevent_update_paragraph_style(self) -> None:
        """Prevent the update of paragraph style."""
    def length(self) -> int:
        """Length of the content.

        Used to update the cursor position after pasting.

        Returns:
            int: The length of the content that was pasted.
        """
    def paste(self, index: int, segment_id: str = None) -> list[dict]:
        """Generate the batch update request for pasting the content in specified index and segment.

        Args:
            index: The index where the content will be pasted.
            segment_id: The segment ID for the content.

        Returns:
            List of dictionaries representing the batch update request.
        """
    def get_footnotes_post_requests(self) -> list[list[StructuralElement]]:
        """Get the footnotes post requests.

        This method is used to get the footnotes post requests from the paragraph elements.
        Because the footnotes content can only be created after the footnote reference is created (we need
        the footnote ID).

        Returns:
            List[List[StructuralElement]]: List of footnotes post requests.
        """
