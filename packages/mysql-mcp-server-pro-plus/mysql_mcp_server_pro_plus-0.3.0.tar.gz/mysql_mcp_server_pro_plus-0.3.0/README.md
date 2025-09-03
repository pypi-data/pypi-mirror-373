# MySQL MCP Server Pro Plus

A robust, secure, and feature-rich Model Context Protocol (MCP) server for MySQL databases. This server provides a standardized interface for AI assistants to interact with MySQL databases through tools and resources.

## 🚀 Features

### Core Features

#### Security & Reliability
- **Secure Database Operations**: Input validation, SQL injection protection, and query sanitization
- **Enterprise Security**: Advanced security validation with configurable security levels
- **Connection Pooling**: Efficient connection management with configurable pool settings
- **Comprehensive Error Handling**: Detailed error messages and proper exception handling
- **Resource Management**: Proper cleanup of database connections and cursors

#### Performance & Monitoring
- **Async/Await Support**: Modern async patterns for better performance
- **Enterprise Monitoring**: Database health analysis, performance metrics, and alerting
- **Query Performance Analysis**: EXPLAIN plan analysis and optimization recommendations
- **Lock Contention Analysis**: Blocking queries detection and resolution guidance
- **Schema Visualization**: ER diagrams and relationship mapping

#### Development & Testing
- **Type Safety**: Full type annotations and Pydantic models for configuration validation
- **Comprehensive Testing**: Unit tests, security tests, and integration tests
- **Test Data Generation**: Comprehensive e-commerce database simulation with 10M+ rows and bad practices for MCP agent testing
- **Interactive Exploration**: Advanced data exploration with drill-down capabilities
- **CI/CD Integration**: Pre-commit hooks, security scanning, and automated testing

### Tools Available

#### Core Database Tools
- **`execute_sql`**: Execute custom SQL queries with result formatting, security validation, and SQL injection protection
- **`list_tables`**: List all tables in the database with basic metadata
- **`describe_table`**: Get detailed table structure information including columns, indexes, constraints, and statistics

#### Advanced Analysis Tools
- **`analyze_db_health`**: Enterprise-grade database health monitoring covering:
  - Index health and usage statistics
  - Connection pool status and limits
  - Replication status and lag monitoring
  - Buffer pool efficiency analysis
  - Constraint integrity validation
  - Auto-increment sequence analysis
  - Table fragmentation assessment
  - Comprehensive performance metrics

- **`analyze_query_performance`**: Query performance analysis and optimization:
  - EXPLAIN plan analysis with execution strategy insights
  - Performance metrics and cost estimation
  - Index recommendations and optimization suggestions
  - Query rewrite suggestions and JOIN optimization
  - Execution analysis with runtime statistics
  - Resource consumption predictions

- **`get_blocking_queries`**: Lock contention and blocking queries analysis:
  - Lock wait graph visualization
  - Deadlock detection and prevention
  - Session termination recommendations
  - Lock timeout configuration suggestions
  - Historical blocking analysis
  - MySQL PERFORMANCE_SCHEMA integration

#### Database Exploration Tools
- **`explore_interactive`**: Interactive data exploration with multiple analysis modes:
  - Drill-down exploration capabilities
  - Smart sampling for large datasets
  - Pattern discovery and anomaly detection
  - Relationship navigation and analysis
  - Time-series analysis for temporal data
  - Comparative analysis across tables
  - Data quality assessment

- **`get_database_overview`**: Comprehensive database overview:
  - Schema analysis and table relationships
  - Performance and security analysis
  - Statistical sampling for large datasets
  - Data quality metrics and insights
  - Security vulnerability assessment

- **`get_schema_visualization`**: Schema visualization and relationship mapping:
  - ER diagram generation (ASCII/text-based)
  - Table dependency analysis
  - Foreign key relationship mapping
  - Constraint visualization (primary keys, unique constraints)
  - Circular reference detection
  - Impact analysis for schema changes

### Resources

- **Table Data**: Access table contents as CSV-formatted resources via `mysql://{table_name}/data`
- **Automatic Discovery**: Dynamic table listing and resource creation
- **Schema Resources**: Database schema information and metadata access

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
│       ├── server.py              # Main MCP server implementation
│       ├── config.py              # Configuration management
│       ├── db_manager.py          # Database connection and management
│       ├── logger.py              # Logging configuration
│       ├── schema_mapping.py      # Schema analysis utilities
│       ├── validator.py           # Security validation
│       └── tools/                 # MCP Tools directory
│           ├── __init__.py
│           ├── analyze_db_health.py          # Database health analysis
│           ├── analyze_query_performance.py # Query performance analysis
│           ├── describe_table.py             # Enhanced table description
│           ├── discover_sensitive_data.py    # Sensitive data discovery (reference)
│           ├── execute_sql.py                # SQL execution tool
│           ├── explore_interactive.py        # Interactive data exploration
│           ├── get_blocking_queries.py       # Blocking queries analysis
│           ├── get_database_overview.py      # Database overview tool
│           ├── get_schema_visualization.py   # Schema visualization
│           └── list_tables.py                # Table listing tool
├── tests/
│   ├── conftest.py             # Test configuration
│   └── test_server.py         # Server unit tests
├── scripts/
│   ├── generate_test_data.py   # Test data generator (10M+ rows)
│   ├── security/
│   │   ├── bandit-docker.sh    # Security scanning with Bandit
│   │   ├── check-secrets.sh    # Secret detection
│   │   └── verify_bad_practices.py # Bad practices verification
├── init-scripts/
│   └── 01-init.sql            # Database initialization with bad practices
├── data/
│   └── mysql/                 # MySQL data directory
├── mysql-config/
│   └── my.cnf                 # MySQL configuration
├── hooks/
│   ├── post_gen_project.py    # Post-generation hooks
│   ├── pre-commit-check-dependencies.sh
│   ├── pre-commit-check-secrets.sh
│   └── pre-commit-run-tests.sh
├── dist/                      # Distribution packages
├── logs/                      # Application logs
├── docker-compose.yml         # Docker Compose configuration
├── Dockerfile                 # Docker image definition
├── pyproject.toml            # Project configuration (Poetry)
├── uv.lock                   # Dependency lock file
├── pytest.ini               # Pytest configuration
├── test_security.py          # Security tests
├── Makefile                  # Build automation
├── env.example              # Environment variables template
├── .env                      # Local environment (gitignored)
├── CHANGELOG.md             # Change log
├── LICENSE                  # MIT License
└── README.md                # This file
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

### Security Features

The project includes comprehensive security features for production deployment:

#### Automated Security Scanning
- **Bandit Integration**: Automated Python security vulnerability scanning
- **Secret Detection**: Pre-commit hooks to prevent accidental secret commits
- **Security Testing**: Dedicated security test suite in `test_security.py`

#### Security Tools
- **Sensitive Data Discovery**: Pattern-based detection of PII, financial data, and sensitive information
- **Security Validation**: Configurable security levels for different deployment environments
- **SQL Injection Protection**: Advanced query validation and sanitization

#### Security Scripts
```bash
# Run comprehensive security checks
make security-check

# Run security tests (standalone)
python -m pytest test_security.py -v

# Check for secrets in code
./scripts/security/check-secrets.sh
```

### Code Quality

The project follows strict code quality standards:

- **Type Annotations**: Full type hints for better IDE support and error detection
- **Pydantic Models**: Data validation and serialization
- **Async/Await**: Modern Python async patterns
- **Error Handling**: Comprehensive exception handling
- **Documentation**: Detailed docstrings and comments
- **Security Scanning**: Automated security vulnerability detection with Bandit
- **Pre-commit Hooks**: Code quality checks and secret detection
- **Comprehensive Testing**: Unit tests, integration tests, and security tests

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
