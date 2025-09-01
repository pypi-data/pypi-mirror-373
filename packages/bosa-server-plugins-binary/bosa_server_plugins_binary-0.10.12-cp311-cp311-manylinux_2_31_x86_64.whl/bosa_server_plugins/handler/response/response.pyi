from _typeshed import Incomplete
from pydantic import BaseModel
from typing import Generic, TypeVar

T = TypeVar('T')
K = TypeVar('K')

class ApiResponse(BaseModel, Generic[T, K]):
    """API Response Entity."""
    model_config: Incomplete
    data: T
    meta: K | None
