import abc
from abc import abstractmethod
from pydantic import BaseModel
from typing import Any, TypeVar

T = TypeVar('T', bound='GQLBaseModel')

class GQLBaseModel(BaseModel, metaclass=abc.ABCMeta):
    """Base GQL model for fragments."""
    @classmethod
    def from_dict(cls, data: dict) -> T | None:
        """Create a GQLBaseModel from a dictionary.

        Args:
            cls: The class to create the model from.
            data: The dictionary to create the model from.

        Returns:
            Optional[T]: The created model.
        """
    @classmethod
    @abstractmethod
    def mapping(cls, data: dict) -> dict[str, Any]:
        """Create a mapping from a dictionary.

        Args:
            cls: The class to create the mapping from.
            data: The dictionary to create the mapping from.

        Returns:
            dict[str, Any]: The created mapping.
        """
