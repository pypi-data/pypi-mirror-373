# MySQL MCP Server Pro Plus

A robust, secure, and feature-rich Model Context Protocol (MCP) server for MySQL databases. This server provides a standardized interface for AI assistants to interact with MySQL databases through tools and resources.

## 🚀 Features

### Core Features

- **Secure Database Operations**: Input validation, SQL injection protection, and query sanitization
- **Connection Pooling**: Efficient connection management with configurable pool settings
- **Type Safety**: Full type annotations and Pydantic models for configuration validation
- **Comprehensive Error Handling**: Detailed error messages and proper exception handling
- **Async/Await Support**: Modern async patterns for better performance
- **Resource Management**: Proper cleanup of database connections and cursors
- **Test Data Generation**: Comprehensive e-commerce database simulation with 10M+ rows and bad practices for MCP agent testing

### Tools Available

- `execute_sql`: Execute custom SQL queries with result formatting
- `list_tables`: List all tables in the database
- `describe_table`: Get detailed table structure information

### Resources

- **Table Data**: Access table contents as CSV-formatted resources
- **Automatic Discovery**: Dynamic table listing and resource creation

## 📋 Requirements

- Python 3.8+
- MySQL 5.7+ or MariaDB 10.2+
- mysql-connector-python

## 🛠️ Installation

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd mysql_mcp_server_pro_plus
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp env.example .env
   # Edit .env with your MySQL configuration
   ```

## ⚙️ Configuration

### Environment Variables

| Variable                   | Description                      | Default              | Required |
| -------------------------- | -------------------------------- | -------------------- | -------- |
| `MYSQL_URL`                | MySQL connection URL (preferred) | -                    | **No\*** |
| `MYSQL_HOST`               | MySQL server host                | `localhost`          | No       |
| `MYSQL_PORT`               | MySQL server port                | `3306`               | No       |
| `MYSQL_USER`               | MySQL username                   | -                    | **Yes**  |
| `MYSQL_PASSWORD`           | MySQL password                   | -                    | **Yes**  |
| `MYSQL_DATABASE`           | MySQL database name              | -                    | **Yes**  |
| `MYSQL_CHARSET`            | Character set                    | `utf8mb4`            | No       |
| `MYSQL_COLLATION`          | Collation                        | `utf8mb4_unicode_ci` | No       |
| `MYSQL_AUTOCOMMIT`         | Auto-commit mode                 | `true`               | No       |
| `MYSQL_SQL_MODE`           | SQL mode                         | `TRADITIONAL`        | No       |
| `MYSQL_CONNECTION_TIMEOUT` | Connection timeout (seconds)     | `10`                 | No       |
| `MYSQL_POOL_SIZE`          | Connection pool size             | `5`                  | No       |
| `MYSQL_POOL_RESET_SESSION` | Reset session on return          | `true`               | No       |

**Note:** Either `MYSQL_URL` or the individual `MYSQL_USER`, `MYSQL_PASSWORD`, and `MYSQL_DATABASE` variables are required. If `MYSQL_URL` is provided, it takes precedence over individual variables.

### Example Configuration

```bash
# .env file

# Option 1: Using MySQL URL (Recommended)
MYSQL_URL=mysql://myuser:mypassword@localhost:3306/mydatabase?charset=utf8mb4&collation=utf8mb4_unicode_ci&sql_mode=TRADITIONAL

# Option 2: Using individual variables
# MYSQL_HOST=localhost
# MYSQL_PORT=3306
# MYSQL_USER=myuser
# MYSQL_PASSWORD=mypassword
# MYSQL_DATABASE=mydatabase
# MYSQL_CHARSET=utf8mb4
# MYSQL_COLLATION=utf8mb4_unicode_ci
# MYSQL_AUTOCOMMIT=true
# MYSQL_SQL_MODE=TRADITIONAL
# MYSQL_CONNECTION_TIMEOUT=10
# MYSQL_POOL_SIZE=5
# MYSQL_POOL_RESET_SESSION=true
```

## 📊 Performance

### Optimizations

- **Connection Pooling**: Reuses database connections for better performance
- **Async Operations**: Non-blocking database operations
- **Efficient Query Execution**: Optimized query handling and result processing
- **Memory Management**: Proper cleanup prevents memory leaks

### Monitoring

- **Comprehensive Logging**: Detailed logs for debugging and monitoring
- **Error Tracking**: Structured error reporting with context
- **Performance Metrics**: Connection and query performance tracking

## 🔧 Development

### Project Structure

```
mysql_mcp_server_pro_plus/
├── src/
│   └── mysql_mcp_server_pro_plus/
│       ├── __init__.py
│       └── server.py          # Main server implementation
├── tests/
│   ├── conftest.py           # Test configuration
│   └── test_server.py        # Server tests
├── scripts/
│   └── generate_test_data.py # Test data generator (10M+ rows)
├── init-scripts/
│   └── 01-init.sql          # Database initialization with bad practices
├── docker-compose.yml        # Docker Compose configuration
├── Dockerfile               # Docker image definition
├── pyproject.toml           # Project configuration
├── requirements.txt         # Python dependencies
├── README.md               # This file
└── README-TEST-DATA.md     # Test data generation documentation
```

### Test Data Generation

For comprehensive MCP agent testing, the project includes a sophisticated test data generation system:

- **Complex E-commerce Database**: 8 interconnected tables with realistic relationships
- **10+ Million Rows**: Distributed across users, products, orders, reviews, and payments
- **1 Million Transactions**: Mixed SELECT, INSERT, UPDATE, and DELETE operations
- **Intentional Bad Practices**: Security vulnerabilities, performance issues, and design flaws for MCP agent detection

See [README-TEST-DATA.md](README-TEST-DATA.md) for detailed documentation.

**Quick Start:**

```bash
# Start the database
make up

# Generate test data (Docker)
make generate-test-data-docker

# Or generate locally
make generate-test-data

# Verify bad practices
make verify-bad-practices-docker
```

### Code Quality

The project follows strict code quality standards:

- **Type Annotations**: Full type hints for better IDE support and error detection
- **Pydantic Models**: Data validation and serialization
- **Async/Await**: Modern Python async patterns
- **Error Handling**: Comprehensive exception handling
- **Documentation**: Detailed docstrings and comments

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 🐛 Troubleshooting

### Common Issues

#### Connection Errors

```
Error: Missing required database configuration
```

**Solution:** Ensure all required environment variables are set. Either provide MYSQL_URL or the individual variables (MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE).

#### Permission Errors

```
Error: Access denied for user
```

**Solution:** Check MySQL user permissions and ensure the user has access to the specified database.

#### Character Set Issues

```
Error: Unknown collation
```

**Solution:** Update MYSQL_CHARSET and MYSQL_COLLATION to values supported by your MySQL version.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Support

For support and questions:

1. Check the [troubleshooting section](#-troubleshooting)
2. Review the [test files](tests/) for usage examples
3. Open an issue on GitHub
4. Check the [CHANGELOG.md](CHANGELOG.md) for recent updates

## 🔄 Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed history of changes and improvements.
