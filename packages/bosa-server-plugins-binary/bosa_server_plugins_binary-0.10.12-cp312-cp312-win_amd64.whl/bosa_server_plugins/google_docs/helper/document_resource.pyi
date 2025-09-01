from _typeshed import Incomplete
from bosa_server_plugins.common.dict import combine_dict_recursive as combine_dict_recursive
from typing import Any

DEFAULT_BULLET_PRESET: str
NESTING_FORMAT: Incomplete
GLYPH_PRESET_TREE: Incomplete

class DocumentResources:
    """Document resources and metadata for the copy content request."""
    styles: Incomplete
    inline_images: Incomplete
    footnotes: Incomplete
    list_bullet_formats: Incomplete
    def __init__(self, styles: dict, inline_images: dict, footnotes: dict, list_bullet_formats: dict) -> None:
        """Initialize the document resources.

        Args:
            styles (Dict): The template styles of the document.
            inline_images (Dict): The inline images of the document.
            footnotes (Dict): The footnotes of the document.
            list_bullet_formats (Dict): The list bullet formats of the document.
        """

def get_document_resources(document_data: dict[str, Any]) -> DocumentResources:
    """Get the document resources for the copy content request.

    Args:
        document_data (Dict[str, Any]): The google docs document data from documents().get().

    Returns:
        DocumentResources: The document resources.
    """
