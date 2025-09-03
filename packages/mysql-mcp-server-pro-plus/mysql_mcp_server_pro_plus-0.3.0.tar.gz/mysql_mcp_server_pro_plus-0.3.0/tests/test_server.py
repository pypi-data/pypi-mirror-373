import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# Import the core classes and functions
from mysql_mcp_server_pro_plus.server import (
    DatabaseManager,
    SecurityValidator,
    DatabaseConfig,
)
from mysql_mcp_server_pro_plus.db_manager import QueryResult


class TestDatabaseConfig:
    """Test DatabaseConfig model validation and creation."""

    def test_database_config_creation(self):
        """Test creating DatabaseConfig with valid parameters."""
        config = DatabaseConfig(user="testuser", password="testpass", database="testdb")

        assert config.user == "testuser"
        assert config.password == "testpass"
        assert config.database == "testdb"
        assert config.host == "localhost"  # default
        assert config.port == 3306  # default

    def test_database_config_from_env_success(self):
        """Test creating DatabaseConfig from environment variables."""
        with patch.dict(
            os.environ,
            {
                "MYSQL_USER": "testuser",
                "MYSQL_PASSWORD": "testpass",
                "MYSQL_DATABASE": "testdb",
                "MYSQL_HOST": "testhost",
                "MYSQL_PORT": "3307",
            },
        ):
            config = DatabaseConfig.from_env()

            assert config.user == "testuser"
            assert config.password == "testpass"
            assert config.database == "testdb"
            assert config.host == "testhost"
            assert config.port == 3307

    def test_database_config_from_env_missing_required(self):
        """Test DatabaseConfig.from_env raises error when required vars are missing."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(
                ValueError, match="Missing required database configuration"
            ):
                DatabaseConfig.from_env()

    def test_database_config_from_env_partial_missing(self):
        """Test DatabaseConfig.from_env raises error when some required vars are missing."""
        with patch.dict(
            os.environ,
            {
                "MYSQL_USER": "testuser",
                "MYSQL_PASSWORD": "testpass",
                # Missing MYSQL_DATABASE
            },
        ):
            with pytest.raises(
                ValueError, match="Missing required database configuration"
            ):
                DatabaseConfig.from_env()


class TestQueryResult:
    """Test QueryResult model."""

    def test_query_result_with_results(self):
        """Test QueryResult with query results."""
        result = QueryResult(
            columns=["id", "name"],
            rows=[[1, "Alice"], [2, "Bob"]],
            row_count=2,
            has_results=True,
        )

        assert result.columns == ["id", "name"]
        assert result.rows == [[1, "Alice"], [2, "Bob"]]
        assert result.row_count == 2
        assert result.has_results is True

    def test_query_result_no_results(self):
        """Test QueryResult without query results."""
        result = QueryResult(columns=[], rows=[], row_count=5, has_results=False)

        assert result.columns == []
        assert result.rows == []
        assert result.row_count == 5
        assert result.has_results is False


class TestSecurityValidator:
    """Test SecurityValidator input validation and sanitization."""

    def test_validate_uri_valid(self):
        """Test validating a valid MySQL URI."""
        uri = "mysql://users/data"
        table_name, path = SecurityValidator.validate_uri(uri)

        assert table_name == "users"
        assert path == "data"

    def test_validate_uri_invalid_scheme(self):
        """Test validating URI with invalid scheme."""
        uri = "http://users/data"
        with pytest.raises(ValueError, match="Invalid URI scheme"):
            SecurityValidator.validate_uri(uri)

    def test_validate_uri_invalid_format(self):
        """Test validating URI with invalid format."""
        uri = "mysql://"
        with pytest.raises(ValueError, match="Invalid URI format"):
            SecurityValidator.validate_uri(uri)

    def test_validate_uri_invalid_table_name(self):
        """Test validating URI with invalid table name."""
        uri = "mysql://users-table/data"
        with pytest.raises(ValueError, match="Invalid table name in URI"):
            SecurityValidator.validate_uri(uri)

    def test_is_valid_table_name_valid(self):
        """Test valid table name validation."""
        valid_names = ["users", "user_data", "data_2024", "test123"]
        for name in valid_names:
            assert SecurityValidator._is_valid_table_name(name) is True

    def test_is_valid_table_name_invalid(self):
        """Test invalid table name validation."""
        invalid_names = [
            "user-data",
            "user.data",
            "user data",
            "user@data",
            "user;data",
        ]
        for name in invalid_names:
            assert SecurityValidator._is_valid_table_name(name) is False

    def test_validate_query_valid(self):
        """Test validating a valid SQL query."""
        query = "SELECT * FROM users WHERE active = 1"
        result = SecurityValidator.validate_query(query)

        assert result == "SELECT * FROM users WHERE active = 1"

    def test_validate_query_empty(self):
        """Test validating an empty query."""
        with pytest.raises(ValueError, match="Query cannot be empty"):
            SecurityValidator.validate_query("")

    def test_validate_query_whitespace_only(self):
        """Test validating a whitespace-only query."""
        with pytest.raises(ValueError, match="Query cannot be empty"):
            SecurityValidator.validate_query("   ")

    def test_validate_query_dangerous_keywords(self):
        """Test validating query with dangerous keywords (should block with error)."""
        dangerous_queries = [
            ("DROP TABLE users", "DROP"),
            ("DELETE FROM users", "DELETE"),
            ("TRUNCATE TABLE users", "TRUNCATE"),
            ("ALTER TABLE users ADD COLUMN test INT", "ALTER"),
            ("CREATE TABLE test (id INT)", "CREATE"),
            ("INSERT INTO users VALUES (1, 'test')", "INSERT"),
            ("UPDATE users SET name = 'test'", "UPDATE"),
            ("GRANT ALL ON *.* TO 'user'@'localhost'", "GRANT"),
            ("REVOKE ALL ON *.* FROM 'user'@'localhost'", "REVOKE"),
            ("EXECUTE stmt", "EXECUTE"),
            ("PREPARE stmt FROM 'SELECT * FROM users'", "PREPARE"),
        ]

        for query, keyword in dangerous_queries:
            # Should raise ValueError with blocked message
            with pytest.raises(
                ValueError,
                match=f"Blocked potentially dangerous SQL operation: {keyword}",
            ):
                SecurityValidator.validate_query(query)


class TestDatabaseManager:
    """Test DatabaseManager database operations."""

    @pytest.fixture
    def db_config(self):
        """Create a test database configuration."""
        return DatabaseConfig(user="testuser", password="testpass", database="testdb")

    @pytest.fixture
    def db_manager(self, db_config):
        """Create a test database manager."""
        return DatabaseManager(db_config)

    def test_get_connection_params(self, db_manager):
        """Test getting connection parameters."""
        params = db_manager._get_connection_params()

        assert params["host"] == "localhost"
        assert params["port"] == 3306
        assert params["user"] == "testuser"
        assert params["password"] == "testpass"
        assert params["database"] == "testdb"
        assert params["charset"] == "utf8mb4"
        assert params["collation"] == "utf8mb4_unicode_ci"
        assert params["autocommit"] is True
        assert params["sql_mode"] == "TRADITIONAL"
        assert params["connection_timeout"] == 10
        assert params["pool_size"] == 5
        assert params["pool_reset_session"] is True

    def test_is_valid_table_name_valid(self, db_manager):
        """Test valid table name validation."""
        valid_names = ["users", "user_data", "data_2024", "test123"]
        for name in valid_names:
            assert db_manager._is_valid_table_name(name) is True

    def test_is_valid_table_name_invalid(self, db_manager):
        """Test invalid table name validation."""
        invalid_names = [
            "user-data",
            "user.data",
            "user data",
            "user@data",
            "user;data",
        ]
        for name in invalid_names:
            assert db_manager._is_valid_table_name(name) is False

    @pytest.mark.asyncio
    async def test_get_tables_success(self, db_manager):
        """Test getting tables successfully."""
        # Mock the execute_query method
        db_manager.execute_query = AsyncMock(
            return_value=QueryResult(
                columns=["Tables_in_testdb"],
                rows=[["users"], ["products"], ["orders"]],
                row_count=3,
                has_results=True,
            )
        )

        tables = await db_manager.get_tables()

        assert tables == ["users", "products", "orders"]
        db_manager.execute_query.assert_called_once_with("SHOW TABLES")

    @pytest.mark.asyncio
    async def test_get_tables_no_results(self, db_manager):
        """Test getting tables when no tables exist."""
        db_manager.execute_query = AsyncMock(
            return_value=QueryResult(
                columns=[], rows=[], row_count=0, has_results=False
            )
        )

        tables = await db_manager.get_tables()

        assert tables == []

    @pytest.mark.asyncio
    async def test_get_table_data_success(self, db_manager):
        """Test getting table data successfully."""
        db_manager.execute_query = AsyncMock(
            return_value=QueryResult(
                columns=["id", "name", "email"],
                rows=[[1, "Alice", "alice@example.com"], [2, "Bob", "bob@example.com"]],
                row_count=2,
                has_results=True,
            )
        )

        result = await db_manager.get_table_data("users")

        assert result.columns == ["id", "name", "email"]
        assert result.rows == [
            [1, "Alice", "alice@example.com"],
            [2, "Bob", "bob@example.com"],
        ]
        assert result.row_count == 2
        assert result.has_results is True

        # Check that the query was constructed correctly
        db_manager.execute_query.assert_called_once_with(
            "SELECT * FROM `users` LIMIT 100"
        )

    @pytest.mark.asyncio
    async def test_get_table_data_invalid_table_name(self, db_manager):
        """Test getting table data with invalid table name."""
        with pytest.raises(ValueError, match="Invalid table name"):
            await db_manager.get_table_data("user-data")

    @pytest.mark.asyncio
    async def test_execute_query_with_results(self, db_manager):
        """Test executing a query that returns results."""
        # Mock the connection and cursor
        mock_cursor = MagicMock()
        mock_cursor.description = [("id",), ("name",)]
        mock_cursor.fetchall.return_value = [[1, "Alice"], [2, "Bob"]]
        mock_cursor.rowcount = 2

        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor

        with patch(
            "mysql_mcp_server_pro_plus.server.connect", return_value=mock_connection
        ):
            result = await db_manager.execute_query("SELECT * FROM users")

            assert result.columns == ["id", "name"]
            assert result.rows == [[1, "Alice"], [2, "Bob"]]
            assert result.row_count == 2
            assert result.has_results is True

    @pytest.mark.asyncio
    async def test_execute_query_no_results(self, db_manager):
        """Test executing a query that doesn't return results."""
        # Mock the connection and cursor
        mock_cursor = MagicMock()
        mock_cursor.description = None
        mock_cursor.rowcount = 5

        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor

        with patch(
            "mysql_mcp_server_pro_plus.server.connect", return_value=mock_connection
        ):
            result = await db_manager.execute_query("UPDATE users SET active = 1")

            assert result.columns == []
            assert result.rows == []
            assert result.row_count == 5
            assert result.has_results is False

            # Check that commit was called
            mock_connection.commit.assert_called_once()


class TestConfiguration:
    """Test configuration loading and validation."""

    def test_get_db_config_success(self):
        """Test getting database configuration successfully."""
        with patch.dict(
            os.environ,
            {
                "MYSQL_USER": "testuser",
                "MYSQL_PASSWORD": "testpass",
                "MYSQL_DATABASE": "testdb",
            },
        ):
            config = DatabaseConfig.from_env()

            assert config.user == "testuser"
            assert config.password == "testpass"
            assert config.database == "testdb"

    def test_get_db_config_missing_required(self):
        """Test getting database configuration with missing required variables."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(
                ValueError, match="Missing required database configuration"
            ):
                DatabaseConfig.from_env()

    def test_get_db_config_error_handling(self):
        """Test error handling in get_db_config."""
        with patch(
            "mysql_mcp_server_pro_plus.server.DatabaseConfig.from_env"
        ) as mock_from_env:
            mock_from_env.side_effect = Exception("Configuration error")

            with pytest.raises(Exception, match="Configuration error"):
                DatabaseConfig.from_env()


class TestIntegration:
    """Integration tests for the complete workflow."""

    @pytest.mark.asyncio
    async def test_complete_workflow(self):
        """Test a complete workflow from configuration to query execution."""
        # Test configuration
        with patch.dict(
            os.environ,
            {
                "MYSQL_USER": "testuser",
                "MYSQL_PASSWORD": "testpass",
                "MYSQL_DATABASE": "testdb",
            },
        ):
            config = DatabaseConfig.from_env()
            assert config.user == "testuser"

            # Test database manager
            db_manager = DatabaseManager(config)
            assert db_manager.config == config

            # Test security validator
            validator = SecurityValidator()

            # Test URI validation
            table_name, path = validator.validate_uri("mysql://users/data")
            assert table_name == "users"
            assert path == "data"

            # Test query validation
            query = validator.validate_query("SELECT * FROM users")
            assert query == "SELECT * FROM users"

            # Test table name validation
            assert validator._is_valid_table_name("users") is True
            assert validator._is_valid_table_name("user-data") is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
