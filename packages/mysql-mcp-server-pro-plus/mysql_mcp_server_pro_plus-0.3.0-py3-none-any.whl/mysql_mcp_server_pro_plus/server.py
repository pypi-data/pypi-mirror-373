from typing import Any, Dict, List, Optional

from fastmcp import FastMCP

from .config import DatabaseConfig
from .db_manager import DatabaseManager
from .logger import logger
from .tools import (
    analyze_db_health_tool,
    analyze_query_performance_tool,
    describe_table_tool,
    execute_sql_tool,
    explore_interactive_tool,
    get_blocking_queries_tool,
    get_database_overview_tool,
    get_schema_visualization_tool,
    list_tables_tool,
)
from .validator import SecurityValidator

# Initialize FastMCP server
mcp = FastMCP("mysql_mcp_server_pro_plus")

# Module-level variables for database managers (initialized when server starts)
_db_manager = None
_security_validator = None


@mcp.resource("mysql://{table_name}/data")
async def read_table_data(table_name: str) -> str:
    """Read data from a MySQL table."""
    try:
        logger.info(f"Reading table data: {table_name}")

        global _db_manager, _security_validator
        if not _db_manager or not _security_validator:
            raise RuntimeError("Server not properly initialized")

        if not _security_validator._is_valid_table_name(table_name):
            raise ValueError(f"Invalid table name: {table_name}")

        result = await _db_manager.get_table_data(table_name)

        if not result.has_results:
            return "No data available"

        # Format results as CSV
        lines = [",".join(result.columns)]
        for row in result.rows:
            lines.append(",".join(str(cell) for cell in row))

        return "\n".join(lines)
    except Exception as e:
        logger.error(f"Error reading table {table_name}: {e}")
        raise RuntimeError(f"Failed to read table: {str(e)}")


@mcp.tool()
async def execute_sql(query: str) -> str:
    """Execute an SQL query on the MySQL server.

    Args:
        query: The SQL query to execute
    """
    global _db_manager, _security_validator
    return await execute_sql_tool(query, _db_manager, _security_validator)


@mcp.tool()
async def list_tables() -> str:
    """List all tables in the database."""
    global _db_manager
    return await list_tables_tool(_db_manager)


@mcp.tool()
async def describe_table(table_name: str) -> str:
    """Describe the structure of a table.

    Args:
        table_name: Name of the table to describe
    """
    global _db_manager, _security_validator
    return await describe_table_tool(table_name, _db_manager, _security_validator)


@mcp.tool()
async def get_database_overview(
    max_tables: int = 500, sampling_mode: bool = True, timeout: int = 300
) -> str:
    """Get comprehensive database overview with performance and security analysis.

    Enterprise-grade comprehensive database assessment providing multi-dimensional analysis:
    - Schema Analysis: Complete structure with table relationships and dependency mapping
    - Performance Metrics: Query performance, index efficiency, and resource utilization patterns
    - Security Analysis: User permissions, role assignments, and security configuration assessment
    - Storage Analysis: Table sizes, index bloat detection, and disk usage optimization
    - Health Indicators: Connection health, vacuum statistics, and system performance metrics

    Args:
        max_tables: Maximum number of tables to analyze per schema (default: 500)
        sampling_mode: Use statistical sampling for large datasets to optimize execution time (default: True)
        timeout: Maximum execution time in seconds with graceful timeout handling (default: 300)
    """
    global _db_manager, _security_validator
    return await get_database_overview_tool(
        _db_manager, _security_validator, max_tables, sampling_mode, timeout
    )


@mcp.tool()
async def get_blocking_queries(timeout: int = 300) -> str:
    """Analyze MySQL blocking queries and lock contention.

    Enterprise-grade blocking queries analysis featuring:
    - Modern Detection: Uses MySQL PERFORMANCE_SCHEMA for accurate blocking identification
    - Lock Hierarchy Visualization: Complete blocking chains and process relationships
    - Comprehensive Metrics: Process details, wait events, timing, lock types, and affected relations
    - Intelligent Recommendations: Severity-based suggestions with specific optimization guidance
    - Production Ready: Designed for enterprise database monitoring and performance troubleshooting

    Analysis Output:
    - Process Information: Thread ID, user, host, database, and connection details
    - Query Context: Full query text, execution timing, and resource consumption
    - Lock Details: Lock types, modes, affected database objects, and wait events
    - State Analysis: Process states, wait information, and blocking duration
    - Trend Analysis: Summary statistics and pattern recognition
    - Categorized Recommendations: 🚨 Critical, ⚠️ Warning, 💡 Optimization, 🎯 Hotspot alerts

    Args:
        timeout: Maximum execution time in seconds (default: 300)
    """
    global _db_manager
    return await get_blocking_queries_tool(_db_manager, timeout)


@mcp.tool()
async def analyze_db_health(timeout: int = 300) -> str:
    """Perform comprehensive MySQL database health analysis.

    Enterprise-grade health monitoring covering:
    - Index Health: Usage statistics, unused indexes, duplicates, and optimization recommendations
    - Connection Pool: Current usage, limits, thread cache efficiency, and connection issues
    - Buffer Pool: InnoDB buffer pool efficiency, hit ratios, and memory utilization
    - Replication: Master/slave status, lag monitoring, and replication health
    - Constraints: Foreign key integrity, constraint violations, and orphaned records
    - Auto-increment: Sequence analysis, exhaustion warnings, and capacity planning
    - Fragmentation: Table fragmentation analysis and optimization candidates
    - Performance: Query cache, slow queries, table locks, and key efficiency metrics
    - Storage Engines: Engine distribution, MyISAM vs InnoDB analysis
    - Security: User accounts, SSL status, and security configuration review

    Health Scoring:
    - Overall health score (0-100) with section-specific scoring
    - 🚨 Critical issues requiring immediate attention
    - ⚠️ Warnings for potential problems
    - 💡 Optimization recommendations for performance improvements
    - 🎯 Hotspot identification for proactive maintenance

    Args:
        timeout: Maximum execution time in seconds (default: 300)
    """
    global _db_manager
    return await analyze_db_health_tool(_db_manager, timeout)


@mcp.tool()
async def analyze_query_performance(
    query: str, analyze_execution: bool = False, timeout: int = 300
) -> str:
    """Analyze query performance with comprehensive metrics and optimization recommendations.

    Enterprise-grade query performance analysis featuring:
    - EXPLAIN Plan Analysis: Query execution strategy, index usage, table scan types
    - Performance Metrics: Estimated vs actual execution time, I/O costs, memory usage
    - Index Recommendations: Missing indexes, unused indexes, composite index suggestions
    - Query Optimization: Rewrite suggestions, JOIN optimization, WHERE clause improvements
    - Execution Analysis: Actual runtime statistics (optional, with safety controls)
    - Cost Estimation: Resource consumption predictions

    Enhanced Features:
    - Query Plan Visualization: ASCII tree structure of execution steps
    - Performance Comparison: Before/after optimization suggestions
    - Resource Usage Tracking: Buffer pool hits, temporary table usage
    - Lock Analysis: Query lock requirements and potential conflicts
    - Cardinality Estimation: Accuracy analysis and statistics recommendations

    Args:
        query: The SQL query to analyze
        analyze_execution: Enable actual execution analysis (default: False, safer)
        timeout: Maximum execution time in seconds (default: 300)
    """
    global _db_manager, _security_validator
    return await analyze_query_performance_tool(
        query, analyze_execution, _db_manager, _security_validator, timeout
    )


@mcp.tool()
async def get_schema_visualization(
    schema_name: Optional[str] = None, format: str = "text", timeout: int = 300
) -> str:
    """Generate comprehensive schema visualization with ER diagrams and relationship analysis.

    Enterprise-grade schema visualization featuring:
    - ER Diagram Generation: ASCII/text-based relationship diagrams
    - Table Dependencies: Foreign key relationships, dependency chains
    - Relationship Types: One-to-one, one-to-many, many-to-many mappings
    - Constraint Visualization: Primary keys, unique constraints, check constraints
    - Circular Reference Detection: Identify potential design issues
    - Impact Analysis: Show cascading effects of schema changes

    Enhanced Features:
    - Schema Statistics: Table sizes, row counts, index usage
    - Data Type Analysis: Column types, nullable patterns, defaults
    - Index Coverage: Index efficiency across relationships
    - Normalization Analysis: 1NF, 2NF, 3NF compliance checking
    - Migration Impact: Dependency order for schema changes

    Args:
        schema_name: Specific schema to analyze (default: current database)
        format: Output format - "text", "tree", or "detailed" (default: "text")
        timeout: Maximum execution time in seconds (default: 300)
    """
    global _db_manager, _security_validator
    return await get_schema_visualization_tool(
        schema_name, format, _db_manager, _security_validator, timeout
    )


@mcp.tool()
async def explore_interactive(
    table_name: str,
    exploration_type: str = "drilldown",
    sample_size: int = 1000,
    filters: Optional[Dict[str, Any]] = None,
    group_by: Optional[List[str]] = None,
    order_by: Optional[str] = None,
    time_column: Optional[str] = None,
) -> str:
    """Interactive data exploration with multiple analysis modes.

    Comprehensive exploration tool providing:
    - Drill-down Exploration: Navigate from summary to detailed views
    - Pattern Discovery: Automatic detection of data patterns and anomalies
    - Relationship Exploration: Navigate foreign key relationships interactively
    - Time-series Analysis: Trend analysis for temporal data
    - Comparative Analysis: Compare data across different segments
    - Smart Sampling: Multiple sampling strategies (random, stratified, time-based)

    Args:
        table_name: Target table to explore
        exploration_type: Type of exploration ("drilldown", "patterns", "relationships",
                        "timeseries", "comparative", "sampling")
        sample_size: Number of records to sample (max 10,000)
        filters: Optional filters to apply as dict (e.g., {"status": "active"})
        group_by: Columns to group by for aggregation
        order_by: Column to order results by
        time_column: Column containing temporal data for time-series analysis

    Returns:
        Comprehensive exploration results with insights and recommendations
    """
    global _db_manager, _security_validator
    return await explore_interactive_tool(
        table_name=table_name,
        exploration_type=exploration_type,
        sample_size=sample_size,
        filters=filters,
        group_by=group_by,
        order_by=order_by,
        time_column=time_column,
        db_manager=_db_manager,
        security_validator=_security_validator,
    )


def main():
    """Main entry point to run the MCP server."""
    # Initialize database configuration and managers
    global _db_manager, _security_validator

    try:
        db_config = DatabaseConfig.from_env()
        _db_manager = DatabaseManager(db_config)
        _security_validator = SecurityValidator()

        # Log configuration (without sensitive data)
        logger.info("Starting MySQL MCP server...")
        logger.info(f"Database: {db_config.host}:{db_config.port}/{db_config.database}")
        logger.info(f"Charset: {db_config.charset}, Collation: {db_config.collation}")

        # Check if running in MCP client mode (stdio) or standalone server mode
        import sys

        if len(sys.argv) > 1 and sys.argv[1] == "--stdio":
            # Run in stdio mode for MCP clients like Claude Desktop
            mcp.run(transport="stdio")
        else:
            # Run as HTTP server for standalone use
            mcp.run(
                transport="streamable-http",
                port=8084,
                host="0.0.0.0",
            )

    except Exception as e:
        logger.error(f"Failed to start server: {e}", exc_info=True)
        raise
