from _typeshed import Incomplete
from bosa_server_plugins.google_docs.helper.copy_content.requests.insert_text import InsertText as InsertText
from bosa_server_plugins.google_docs.helper.copy_content.requests.structural_element.base import StructuralElement as StructuralElement
from bosa_server_plugins.google_docs.helper.copy_content.requests.structural_element.bullet_group_paragraph import BulletGroupParagraph as BulletGroupParagraph
from bosa_server_plugins.google_docs.helper.copy_content.requests.structural_element.paragraph import Paragraph as Paragraph
from bosa_server_plugins.google_docs.helper.copy_content.requests.structural_element.table import Table as Table
from bosa_server_plugins.google_docs.services.documents import GoogleDocsDocumentsService as GoogleDocsDocumentsService
from enum import StrEnum

PASTE_LOCATION_START_DOCUMENT_INDEX: int

class PasteLocationCategory(StrEnum):
    """Paste location category for the copy content request."""
    INSIDE_PARAGRAPH = 'inside_paragraph'
    APPEND_PARAGRAPH = 'append_paragraph'
    NEW_PARAGRAPH = 'outside_paragraph'

class DocumentPasteWriter:
    """Executes copy paste content operations in Google Docs."""
    service: Incomplete
    def __init__(self, service: GoogleDocsDocumentsService) -> None:
        """Initialize the DocumentPasteWriter.

        Args:
            service (GoogleDocsDocumentsService): The Google Docs service instance.
        """
    def execute(self, document_id: str, paste_document_body: dict, paste_location: int, batch_update_requests: list[StructuralElement]) -> tuple[int, int]:
        """Execute the paste operation.

        Args:
            document_id (str): The ID of the document.
            paste_document_body (Dict): The body of the destination document.
            paste_location (int): The location to paste the content.
            batch_update_requests (List[StructuralElement]): The list of structural elements to be pasted.

        Returns:
            Tuple[int, int]: The paste location and the end index of the paste location.
        """
