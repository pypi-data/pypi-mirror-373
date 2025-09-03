import re
from typing import Tuple
from .logger import logger


class SecurityValidator:
    """Validates and sanitizes inputs for security."""

    @staticmethod
    def validate_uri(uri: str) -> Tuple[str, str]:
        """Validate and parse MySQL URI."""
        if not uri.startswith("mysql://"):
            raise ValueError(f"Invalid URI scheme: {uri}")

        # Remove mysql:// prefix and split
        path = uri[8:]
        parts = path.split("/")

        if len(parts) < 1 or not parts[0]:
            raise ValueError(f"Invalid URI format: {uri}")

        table_name = parts[0]
        if not SecurityValidator._is_valid_table_name(table_name):
            raise ValueError(f"Invalid table name in URI: {table_name}")

        return table_name, "/".join(parts[1:]) if len(parts) > 1 else ""

    @staticmethod
    def _is_valid_table_name(table_name: str) -> bool:
        """Validate table name to prevent SQL injection."""
        return bool(re.match(r"^[a-zA-Z0-9_]+$", table_name))

    @staticmethod
    def validate_query(query: str) -> str:
        """Validate SQL query for security."""
        query = query.strip()
        if not query:
            raise ValueError("Query cannot be empty")

        # Check for potentially dangerous operations
        dangerous_keywords = [
            "DROP",
            "DELETE",
            "TRUNCATE",
            "ALTER",
            "CREATE",
            "INSERT",
            "UPDATE",
            "GRANT",
            "REVOKE",
            "EXECUTE",
            "PREPARE",
        ]

        query_upper = query.upper()
        for keyword in dangerous_keywords:
            if keyword in query_upper:
                error_msg = f"Blocked potentially dangerous SQL operation: {keyword}. This operation is not allowed for security reasons."
                logger.error(error_msg)
                raise ValueError(error_msg)

        return query
