from _typeshed import Incomplete
from bosa_server_plugins.google_docs.helper.copy_content.requests.create_paragraph_bullet import CreateParagraphBullet as CreateParagraphBullet
from bosa_server_plugins.google_docs.helper.copy_content.requests.insert_text import InsertText as InsertText
from bosa_server_plugins.google_docs.helper.copy_content.requests.structural_element.base import StructuralElement as StructuralElement
from bosa_server_plugins.google_docs.helper.copy_content.requests.structural_element.paragraph import Paragraph as Paragraph
from bosa_server_plugins.google_docs.helper.document_resource import DEFAULT_BULLET_PRESET as DEFAULT_BULLET_PRESET

class BulletGroupParagraph(StructuralElement):
    """Helper class to group paragraph for create paragraph bullet batch update request."""
    elements: Incomplete
    bullet_preset: Incomplete
    def __init__(self, elements: list[tuple[Paragraph, int]], bullet_preset: str | None = ...) -> None:
        """Initialize the BulletGroupParagraph object.

        Args:
            elements (List[Paragraph]): The elements in the paragraph.
            bullet_preset (str): The bullet preset for the paragraph.
        """
    def length(self) -> int:
        """Length of the content.

        Used to update the cursor position after pasting.

        Returns:
            int: The length of the content that was pasted.
        """
    def remove_first_paragraph(self) -> Paragraph:
        """Remove the first paragraph from the group.

        This is used to prevent the first paragraph from being numbered.
        """
    def remove_last_paragraph(self) -> Paragraph:
        """Remove the last paragraph from the group.

        This is used to prevent the last paragraph from being numbered.
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

        Returns:
            List[List[StructuralElement]]: A list of footnotes post requests.
        """
