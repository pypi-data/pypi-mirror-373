import os
from urllib.parse import urlparse, parse_qs

from pydantic import BaseModel, Field


class DatabaseConfig(BaseModel):
    """Database configuration model with validation."""

    host: str = Field(default="localhost", description="MySQL host")
    port: int = Field(default=3306, description="MySQL port")
    user: str = Field(description="MySQL username")
    password: str = Field(description="MySQL password")
    database: str = Field(description="MySQL database name")
    charset: str = Field(default="utf8mb4", description="MySQL charset")
    collation: str = Field(default="utf8mb4_unicode_ci", description="MySQL collation")
    autocommit: bool = Field(default=True, description="Auto-commit mode")
    sql_mode: str = Field(default="TRADITIONAL", description="SQL mode")
    connection_timeout: int = Field(
        default=10, description="Connection timeout in seconds"
    )
    pool_size: int = Field(default=5, description="Connection pool size")
    pool_reset_session: bool = Field(
        default=True, description="Reset session on connection return"
    )

    @classmethod
    def from_url(cls, url: str) -> "DatabaseConfig":
        """Create DatabaseConfig from MySQL connection URL.

        Expected format: mysql://user:password@host:port/database?charset=utf8mb4&collation=utf8mb4_unicode_ci
        """
        parsed = urlparse(url)

        if parsed.scheme not in ("mysql", "mysql+pymysql"):
            raise ValueError(
                f"Invalid URL scheme: {parsed.scheme}. Expected 'mysql' or 'mysql+pymysql'"
            )

        if not all([parsed.username, parsed.password, parsed.path.lstrip("/")]):
            raise ValueError("URL must include username, password, and database name")

        # Parse query parameters
        query_params = parse_qs(parsed.query) if parsed.query else {}

        def get_param(key: str, default: str) -> str:
            return query_params.get(key, [default])[0]

        def get_bool_param(key: str, default: bool) -> bool:
            return get_param(key, str(default)).lower() == "true"

        def get_int_param(key: str, default: int) -> int:
            return int(get_param(key, str(default)))

        return cls(
            host=parsed.hostname or "localhost",
            port=parsed.port or 3306,
            user=parsed.username or "",
            password=parsed.password or "",
            database=parsed.path.lstrip("/"),
            charset=get_param("charset", "utf8mb4"),
            collation=get_param("collation", "utf8mb4_unicode_ci"),
            autocommit=get_bool_param("autocommit", True),
            sql_mode=get_param("sql_mode", "TRADITIONAL"),
            connection_timeout=get_int_param("connection_timeout", 10),
            pool_size=get_int_param("pool_size", 5),
            pool_reset_session=get_bool_param("pool_reset_session", True),
        )

    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        """Create DatabaseConfig from environment variables with validation.

        Supports both MYSQL_URL (preferred) and individual environment variables.
        If MYSQL_URL is provided, it takes precedence over individual variables.
        """
        # Check for connection URL first
        mysql_url = os.getenv("MYSQL_URL")
        if mysql_url:
            return cls.from_url(mysql_url)

        # Fallback to individual environment variables
        user = os.getenv("MYSQL_USER")
        password = os.getenv("MYSQL_PASSWORD")
        database = os.getenv("MYSQL_DATABASE")

        if not all([user, password, database]):
            raise ValueError(
                "Missing required database configuration: Either MYSQL_URL or MYSQL_USER, MYSQL_PASSWORD, and MYSQL_DATABASE are required"
            )

        # At this point, we know user, password, and database are not None
        assert user is not None
        assert password is not None
        assert database is not None

        return cls(
            host=os.getenv("MYSQL_HOST", "localhost"),
            port=int(os.getenv("MYSQL_PORT", "3306")),
            user=user,
            password=password,
            database=database,
            charset=os.getenv("MYSQL_CHARSET", "utf8mb4"),
            collation=os.getenv("MYSQL_COLLATION", "utf8mb4_unicode_ci"),
            autocommit=os.getenv("MYSQL_AUTOCOMMIT", "true").lower() == "true",
            sql_mode=os.getenv("MYSQL_SQL_MODE", "TRADITIONAL"),
            connection_timeout=int(os.getenv("MYSQL_CONNECTION_TIMEOUT", "10")),
            pool_size=int(os.getenv("MYSQL_POOL_SIZE", "5")),
            pool_reset_session=os.getenv("MYSQL_POOL_RESET_SESSION", "true").lower()
            == "true",
        )
