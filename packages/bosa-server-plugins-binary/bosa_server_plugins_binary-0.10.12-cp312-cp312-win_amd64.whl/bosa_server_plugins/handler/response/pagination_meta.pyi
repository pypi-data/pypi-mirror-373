from dataclasses import dataclass

@dataclass
class PaginationMeta:
    """The pagination meta entity."""
    page: int
    limit: int
    total: int
    def __init__(self, page: int, limit: int, total: int) -> None:
        """Constructor."""
