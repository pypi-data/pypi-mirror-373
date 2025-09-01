import abc
from abc import ABC, abstractmethod

DEFAULT_STRUCTURAL_ELEMENT_LENGTH: int

class StructuralElement(ABC, metaclass=abc.ABCMeta):
    """Base class for structural elements in Google Docs API."""
    @abstractmethod
    def length(self) -> int:
        """Length of the content.

        Used to update the cursor position after pasting.

        Returns:
            The length of the content that was pasted.
        """
    @abstractmethod
    def paste(self, index: int, segment_id: str = None) -> list[dict]:
        """Generate the batch update request for pasting the content in specified index and segment.

        Args:
            index: The index where the content will be pasted.
            segment_id: The segment ID for the content.

        Returns:
            List of dictionaries representing the batch update request.
        """
    @abstractmethod
    def get_footnotes_post_requests(self) -> list[list['StructuralElement']]:
        """Get the footnotes post requests.

        This method is used to get the footnotes post requests from the paragraph elements.
        Because the footnotes content can only be created after the footnote reference is created (we need
        the footnote ID).

        Returns:
            List[List[StructuralElement]]: List of footnotes post requests.
        """
