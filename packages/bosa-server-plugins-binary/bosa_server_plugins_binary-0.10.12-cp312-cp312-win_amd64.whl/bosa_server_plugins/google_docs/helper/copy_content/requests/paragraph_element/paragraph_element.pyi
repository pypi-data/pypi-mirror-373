from _typeshed import Incomplete
from bosa_server_plugins.google_docs.helper.copy_content.requests.create_footnote import CreateFootnote as CreateFootnote
from bosa_server_plugins.google_docs.helper.copy_content.requests.insert_inline_image import InsertInlineImage as InsertInlineImage
from bosa_server_plugins.google_docs.helper.copy_content.requests.insert_page_break import InsertPageBreak as InsertPageBreak
from bosa_server_plugins.google_docs.helper.copy_content.requests.insert_text import InsertText as InsertText
from bosa_server_plugins.google_docs.helper.copy_content.requests.update_text_style import UpdateTextStyle as UpdateTextStyle

ParagraphElementType = InsertText | InsertInlineImage | InsertPageBreak | CreateFootnote

class ParagraphElement:
    """Base class for paragraph elements in Google Docs API."""
    element: Incomplete
    style: Incomplete
    def __init__(self, element: ParagraphElementType, style: UpdateTextStyle) -> None:
        """Initialize the ParagraphElement object.

        Args:
            element: The paragraph element to be copied.
            style: The style of the text.
        """
    def get_element(self) -> ParagraphElementType:
        """Get the paragraph element.

        Returns:
            The paragraph element.
        """
    def get_style(self) -> UpdateTextStyle:
        """Get the style of the paragraph element.

        Returns:
            The style of the paragraph element.
        """
