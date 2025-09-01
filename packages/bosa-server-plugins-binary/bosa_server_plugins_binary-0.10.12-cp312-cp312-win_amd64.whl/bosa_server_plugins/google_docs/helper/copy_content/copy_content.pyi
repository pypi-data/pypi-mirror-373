from bosa_server_plugins.google_docs.helper.copy_content.copy_reader import CopyIndex as CopyIndex, DocumentCopyReader as DocumentCopyReader
from bosa_server_plugins.google_docs.helper.copy_content.paste_writer import DocumentPasteWriter as DocumentPasteWriter
from bosa_server_plugins.google_docs.helper.copy_content.requests.insert_page_break import InsertPageBreak as InsertPageBreak
from bosa_server_plugins.google_docs.helper.copy_content.requests.paragraph_element.paragraph_element import ParagraphElement as ParagraphElement
from bosa_server_plugins.google_docs.helper.copy_content.requests.structural_element.paragraph import Paragraph as Paragraph
from bosa_server_plugins.google_docs.helper.copy_content.requests.update_text_style import UpdateTextStyle as UpdateTextStyle
from bosa_server_plugins.google_docs.requests.copy import CopyRequest as CopyRequest
from bosa_server_plugins.google_docs.services.documents import GoogleDocsDocumentsService as GoogleDocsDocumentsService

def copy_content(request: CopyRequest, service: GoogleDocsDocumentsService):
    """Copy content from one document to another.

    Args:
        request (CopyRequest): The request object containing the document ID and indices.
        service (GoogleDocsDocumentsService): The Google Docs service instance.
    """
