from _typeshed import Incomplete
from bosa_server_plugins.google_docs.helper.copy_content.requests.insert_table import InsertTable as InsertTable
from bosa_server_plugins.google_docs.helper.copy_content.requests.structural_element.base import DEFAULT_STRUCTURAL_ELEMENT_LENGTH as DEFAULT_STRUCTURAL_ELEMENT_LENGTH, StructuralElement as StructuralElement
from bosa_server_plugins.google_docs.helper.copy_content.requests.update_table_column_properties import UpdateTableColumnProperties as UpdateTableColumnProperties

TABLE_START_OFFSET_FROM_TRUE_LOCATION: int

class Table(StructuralElement):
    """Google Docs table batch update request."""
    rows: Incomplete
    columns: Incomplete
    column_properties: Incomplete
    contents: Incomplete
    def __init__(self, rows: int, columns: int, column_properties: list[dict], contents: list[list[list[StructuralElement]]]) -> None:
        """Initialize the Table object.

        Args:
            rows: The number of rows in the table.
            columns: The number of columns in the table.
            column_properties: The properties of the columns in the table.
            contents: The content of the table, represented as a list of lists of StructuralElement objects.
        """
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
