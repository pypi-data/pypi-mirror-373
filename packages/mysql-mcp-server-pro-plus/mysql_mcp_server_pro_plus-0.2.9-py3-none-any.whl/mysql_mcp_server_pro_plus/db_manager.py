import re
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

import mysql.connector
from mysql.connector import connect, Error
from pydantic import BaseModel, Field

from .config import DatabaseConfig
from .logger import logger


class QueryResult(BaseModel):
    """Result of a database query."""

    columns: List[str] = Field(description="Column names")
    rows: List[List[Any]] = Field(description="Query results")
    row_count: int = Field(description="Number of rows affected")
    has_results: bool = Field(description="Whether query returned results")


class DatabaseManager:
    """Manages database connections and operations."""

    def __init__(self, config: DatabaseConfig):
        self.config = config
        self._connection_pool: Optional[mysql.connector.pooling.MySQLConnectionPool] = (
            None
        )

    def _get_connection_params(self) -> Dict[str, Any]:
        """Get connection parameters for MySQL."""
        return {
            "host": self.config.host,
            "port": self.config.port,
            "user": self.config.user,
            "password": self.config.password,
            "database": self.config.database,
            "charset": self.config.charset,
            "collation": self.config.collation,
            "autocommit": self.config.autocommit,
            "sql_mode": self.config.sql_mode,
            "connection_timeout": self.config.connection_timeout,
            "pool_size": self.config.pool_size,
            "pool_reset_session": self.config.pool_reset_session,
        }

    @asynccontextmanager
    async def get_connection(self):
        """Get a database connection with proper cleanup."""
        conn = None
        try:
            conn = connect(**self._get_connection_params())
            if conn is None:
                raise ValueError("No connection available")
            logger.debug(f"Connected to MySQL server version: {conn.get_server_info()}")
            yield conn
        except Error as e:
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if conn:
                try:
                    conn.close()
                    logger.debug("Database connection closed")
                except Error as e:
                    logger.warning(f"Error closing connection: {e}")

    @asynccontextmanager
    async def get_cursor(self, connection):
        """Get a database cursor with proper cleanup."""
        cursor = None
        try:
            cursor = connection.cursor()
            yield cursor
        finally:
            if cursor:
                try:
                    cursor.close()
                except Error as e:
                    logger.warning(f"Error closing cursor: {e}")

    async def execute_query(self, query: str) -> QueryResult:
        """Execute a query and return results."""
        async with self.get_connection() as conn:
            if conn is None:
                raise ValueError("No connection available")

            async with self.get_cursor(conn) as cursor:
                try:
                    cursor.execute(query)

                    # Check if query returns results
                    if cursor.description is not None:
                        columns = [desc[0] for desc in cursor.description]
                        rows = cursor.fetchall()
                        return QueryResult(
                            columns=columns,
                            rows=rows,
                            row_count=cursor.rowcount,
                            has_results=True,
                        )
                    else:
                        # Non-SELECT query
                        conn.commit()
                        return QueryResult(
                            columns=[],
                            rows=[],
                            row_count=cursor.rowcount,
                            has_results=False,
                        )
                except Error as e:
                    logger.error(f"Query execution error: {e}")
                    raise

    async def get_tables(self) -> List[str]:
        """Get list of tables in the database."""
        result = await self.execute_query("SHOW TABLES")
        if result.has_results and result.rows:
            return [row[0] for row in result.rows]
        return []

    async def get_table_data(self, table_name: str, limit: int = 100) -> QueryResult:
        """Get data from a specific table."""
        # Validate table name to prevent SQL injection
        if not self._is_valid_table_name(table_name):
            raise ValueError(f"Invalid table name: {table_name}")

        query = f"SELECT * FROM `{table_name}` LIMIT {limit}"
        return await self.execute_query(query)

    def _is_valid_table_name(self, table_name: str) -> bool:
        """Validate table name to prevent SQL injection."""
        # Only allow alphanumeric characters and underscores
        return bool(re.match(r"^[a-zA-Z0-9_]+$", table_name))
