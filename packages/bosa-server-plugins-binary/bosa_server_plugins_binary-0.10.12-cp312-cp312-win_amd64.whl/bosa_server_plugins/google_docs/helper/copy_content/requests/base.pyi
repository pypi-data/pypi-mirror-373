import abc
from abc import ABC, abstractmethod

DEFAULT_ELEMENT_LENGTH: int
NO_CONTENT_LENGTH: int

class BatchUpdateRequest(ABC, metaclass=abc.ABCMeta):
    """Base class for batch update requests in Google Docs API."""
    @abstractmethod
    def length(self) -> int:
        """Length of the content.

        Used to update the cursor position after pasting.

        Returns:
            The length of the content that was pasted.
        """
    @abstractmethod
    def paste(self, index: int, segment_id: str = None) -> dict:
        """Generate the batch update request for pasting the content in specified index and segment.

        Args:
            index: The index where the content will be pasted.
            segment_id: The segment ID for the content.

        Returns:
            A dictionary representing the batch update request.
        """
