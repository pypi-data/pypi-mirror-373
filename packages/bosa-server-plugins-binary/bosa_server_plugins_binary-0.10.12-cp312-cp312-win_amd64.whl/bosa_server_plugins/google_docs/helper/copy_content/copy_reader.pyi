from _typeshed import Incomplete
from bosa_server_plugins.common.dict import combine_dict_recursive as combine_dict_recursive
from bosa_server_plugins.google_docs.helper.copy_content.requests.create_footnote import CreateFootnote as CreateFootnote
from bosa_server_plugins.google_docs.helper.copy_content.requests.insert_inline_image import InsertInlineImage as InsertInlineImage
from bosa_server_plugins.google_docs.helper.copy_content.requests.insert_page_break import InsertPageBreak as InsertPageBreak
from bosa_server_plugins.google_docs.helper.copy_content.requests.insert_text import InsertText as InsertText
from bosa_server_plugins.google_docs.helper.copy_content.requests.paragraph_element.paragraph_element import ParagraphElement as ParagraphElement
from bosa_server_plugins.google_docs.helper.copy_content.requests.structural_element.base import StructuralElement as StructuralElement
from bosa_server_plugins.google_docs.helper.copy_content.requests.structural_element.bullet_group_paragraph import BulletGroupParagraph as BulletGroupParagraph
from bosa_server_plugins.google_docs.helper.copy_content.requests.structural_element.paragraph import Paragraph as Paragraph
from bosa_server_plugins.google_docs.helper.copy_content.requests.structural_element.table import Table as Table
from bosa_server_plugins.google_docs.helper.copy_content.requests.update_text_style import UpdateTextStyle as UpdateTextStyle
from bosa_server_plugins.google_docs.helper.document_resource import DocumentResources as DocumentResources, get_document_resources as get_document_resources
from typing import Any

class CopyIndex:
    """Copy index for the copy content request."""
    start_index: Incomplete
    end_index: Incomplete
    def __init__(self, start_index: int | None = None, end_index: int | None = None) -> None:
        """Initialize the copy index.

        Args:
            start_index (Optional[int]): The start index of the copy.
                If None, it means from the beginning of docs content.
            end_index (Optional[int]): The end index of the copy. If None, it means to the end of docs content.
        """

class DocumentCopyReader:
    """Class for processing document content for copy operations."""
    def read(self, document_data: dict[str, Any], copy_index: CopyIndex) -> tuple[list[StructuralElement], DocumentResources]:
        """Read the document data and return the document resources.

        Args:
            document_data (Dict[str, Any]): The google docs document data from documents().get().
            copy_index (CopyIndex): The copy index for the request.

        Returns:
            Tuple[List[StructuralElement], DocumentResources]: The list of structural elements
                and the document resources.
        """
