from pydantic import BaseModel
from typing import Any

class SqlConfig(BaseModel):
    """Configuration for SQL database connection.

    Either provide a complete `url` or all individual connection parameters.
    """
    url: str | None
    host: str | None
    port: int | None
    database: str | None
    username: str | None
    password: str | None
    driver: str | None
    identifier: str | None
    extra_config: dict[str, Any] | None
    def validate_config(self) -> SqlConfig:
        """Validate that either url or all individual fields are provided.

        Returns:
            SQLConfig: The validated configuration.

        Raises:
            ValueError: If the configuration is invalid.
        """
