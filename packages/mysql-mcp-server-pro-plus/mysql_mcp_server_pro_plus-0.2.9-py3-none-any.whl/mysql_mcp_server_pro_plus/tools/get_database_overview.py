"""Database overview tool for comprehensive MySQL database analysis.

Adapted from the original postgres-mcp project for MySQL compatibility.
"""

from __future__ import annotations

import asyncio
import time
from typing import Any, Dict, List, cast

from ..schema_mapping import SchemaMappingTool
from ..logger import logger


class DatabaseOverviewTool:
    """Tool for generating comprehensive database overview with performance and security analysis."""

    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.max_tables_per_schema = 100  # Limit tables per schema
        self.enable_sampling = True  # Use sampling for large datasets
        self.timeout_seconds = 300  # 5 minute timeout
        self.schema_mapping_tool = SchemaMappingTool(db_manager)

    async def get_database_overview(
        self, max_tables: int = 500, sampling_mode: bool = True, timeout: int = 300
    ) -> str:
        """Get comprehensive database overview with performance and security analysis.

        Args:
            max_tables: Maximum number of tables to analyze per schema (default: 500)
            sampling_mode: Use statistical sampling for large datasets (default: True)
            timeout: Maximum execution time in seconds (default: 300)
        """
        start_time = time.time()
        try:
            # Add timeout wrapper
            result = await asyncio.wait_for(
                self._get_database_overview_internal(
                    max_tables, sampling_mode, start_time
                ),
                timeout=timeout,
            )
            return self._format_as_text(result)
        except asyncio.TimeoutError:
            logger.warning(f"Database overview timed out after {timeout} seconds")
            error_result = {
                "error": f"Operation timed out after {timeout} seconds",
                "execution_metadata": {
                    "max_tables": max_tables,
                    "sampling_mode": sampling_mode,
                    "timeout": timeout,
                    "execution_time": time.time() - start_time,
                },
            }
            return self._format_as_text(error_result)
        except Exception as e:
            logger.error(f"Error generating database overview: {e!s}")
            error_result = {
                "error": str(e),
                "execution_metadata": {
                    "max_tables": max_tables,
                    "sampling_mode": sampling_mode,
                    "timeout": timeout,
                    "execution_time": time.time() - start_time,
                },
            }
            return self._format_as_text(error_result)

    async def _get_database_overview_internal(
        self, max_tables: int, sampling_mode: bool, start_time: float
    ) -> Dict[str, Any]:
        """Internal implementation of database overview."""
        try:
            db_info = {
                "schemas": {},
                "database_summary": {
                    "total_schemas": 0,
                    "total_tables": 0,
                    "total_size_bytes": 0,
                    "total_rows": 0,
                },
                "performance_overview": {},
                "security_overview": {},
                "relationships": {"foreign_keys": [], "relationship_summary": {}},
                "execution_metadata": {
                    "max_tables": max_tables,
                    "sampling_mode": sampling_mode,
                    "timeout": self.timeout_seconds,
                    "tables_analyzed": 0,
                    "tables_skipped": 0,
                },
            }

            # Get database-wide performance metrics
            await self._get_performance_metrics(db_info)

            # Get schema information
            user_schemas = await self._get_user_schemas()
            db_info["database_summary"]["total_schemas"] = len(user_schemas)  # type: ignore

            # Track relationships and table stats
            all_relationships = []
            table_connections = {}
            all_tables_with_stats = []

            # Process each schema with limits
            for schema in user_schemas:
                logger.info(f"Processing schema: {schema}")
                schema_info = await self._process_schema(
                    schema,
                    all_relationships,
                    table_connections,
                    all_tables_with_stats,
                    max_tables,
                    sampling_mode,
                )
                db_info["schemas"][schema] = schema_info  # type: ignore

                # Update database totals
                db_info["database_summary"]["total_tables"] += schema_info[  # type: ignore
                    "table_count"
                ]
                db_info["database_summary"]["total_size_bytes"] += schema_info[  # type: ignore
                    "total_size_bytes"
                ]
                db_info["database_summary"]["total_rows"] += schema_info["total_rows"]  # type: ignore

                # Update metadata
                db_info["execution_metadata"]["tables_analyzed"] += schema_info.get(  # type: ignore
                    "tables_analyzed", 0
                )
                db_info["execution_metadata"]["tables_skipped"] += schema_info.get(  # type: ignore
                    "tables_skipped", 0
                )

            # Add human-readable database size
            total_size_gb = cast(
                int, db_info["database_summary"]["total_size_bytes"]
            ) / (1024**3)  # type: ignore
            db_info["database_summary"]["total_size_readable"] = (
                f"{total_size_gb:.2f} GB"  # type: ignore
            )

            # Add top tables summary
            if all_tables_with_stats:
                await self._add_top_tables_summary(db_info, all_tables_with_stats)

            # Add security overview
            await self._get_security_overview(db_info)

            # Build relationship summary
            await self._build_relationship_summary(
                db_info, all_relationships, table_connections, user_schemas
            )

            # Add schema relationship mapping
            await self._add_schema_relationship_mapping(db_info, user_schemas)

            # Add performance hotspot identification
            await self._identify_performance_hotspots(db_info, all_tables_with_stats)

            # Add execution timing
            execution_time = time.time() - start_time
            db_info["execution_metadata"]["execution_time"] = round(execution_time, 2)  # type: ignore
            logger.info(
                f"Database overview complete: {db_info['database_summary']['total_tables']} tables "
                f"across {len(user_schemas)} schemas, {len(all_relationships)} relationships "
                f"in {execution_time:.2f}s"
            )
            return db_info

        except Exception as e:
            logger.error(f"Error generating database overview: {e!s}")
            return {"error": str(e)}

    async def _get_user_schemas(self) -> List[str]:
        """Get list of user schemas (excluding system schemas)."""
        query = """
            SELECT SCHEMA_NAME as schema_name
            FROM information_schema.SCHEMATA
            WHERE SCHEMA_NAME NOT IN ('information_schema', 'performance_schema', 'mysql', 'sys')
            ORDER BY SCHEMA_NAME
        """
        result = await self.db_manager.execute_query(query)
        if result.has_results:
            return [
                dict(zip(result.columns, row))["schema_name"] for row in result.rows
            ]
        return []

    async def _get_performance_metrics(self, db_info: Dict[str, Any]) -> None:
        """Get database-wide performance metrics."""
        try:
            # Get database size and connection info
            db_stats_query = """
                SELECT
                    ROUND(SUM(data_length + index_length), 0) as database_size_bytes,
                    (SELECT VARIABLE_VALUE FROM information_schema.GLOBAL_STATUS WHERE VARIABLE_NAME = 'Threads_connected') as active_connections,
                    (SELECT VARIABLE_VALUE FROM information_schema.GLOBAL_VARIABLES WHERE VARIABLE_NAME = 'max_connections') as max_connections
                FROM information_schema.TABLES
                WHERE TABLE_SCHEMA NOT IN ('information_schema', 'performance_schema', 'mysql', 'sys')
            """

            result = await self.db_manager.execute_query(db_stats_query)
            if result.has_results and result.rows:
                row_dict = dict(zip(result.columns, result.rows[0]))
                active_conn = int(row_dict.get("active_connections", 0))
                max_conn = int(row_dict.get("max_connections", 1))

                db_info["performance_overview"] = {
                    "active_connections": active_conn,
                    "total_connections": active_conn,  # MySQL doesn't distinguish total vs active easily
                    "max_connections": max_conn,
                    "connection_usage_percent": round((active_conn / max_conn) * 100, 2)
                    if max_conn > 0
                    else 0,
                }
        except Exception as e:
            logger.warning(f"Could not get performance metrics: {e}")
            db_info["performance_overview"] = {
                "active_connections": 0,
                "total_connections": 0,
                "max_connections": 0,
                "connection_usage_percent": 0,
            }

    async def _process_schema(
        self,
        schema: str,
        all_relationships: List[Dict[str, Any]],
        table_connections: Dict[str, int],
        all_tables_with_stats: List[Dict[str, Any]],
        max_tables: int,
        sampling_mode: bool,
    ) -> Dict[str, Any]:
        """Process a single schema and return its information."""
        # Get tables in schema
        tables = await self._get_tables_in_schema(schema)

        # Apply sampling and limits
        tables_to_process = tables
        tables_skipped = 0

        if len(tables) > max_tables:
            if sampling_mode:
                # Sample tables evenly across the list
                step = len(tables) / max_tables
                tables_to_process = [tables[int(i * step)] for i in range(max_tables)]
                tables_skipped = len(tables) - max_tables
                logger.info(
                    f"Schema {schema}: sampling {max_tables} of {len(tables)} tables"
                )
            else:
                # Take first N tables
                tables_to_process = tables[:max_tables]
                tables_skipped = len(tables) - max_tables
                logger.info(
                    f"Schema {schema}: limiting to first {max_tables} of {len(tables)} tables"
                )

        schema_info = {
            "table_count": len(tables),
            "total_size_bytes": 0,
            "total_rows": 0,
            "tables": {},
            "tables_analyzed": len(tables_to_process),
            "tables_skipped": tables_skipped,
            "is_sampled": tables_skipped > 0,
        }

        # Get bulk table statistics
        bulk_stats = await self._get_bulk_table_stats(tables_to_process, schema)
        for table in tables_to_process:
            # Get table stats from bulk query
            table_stats = bulk_stats.get(table, {"row_count": 0, "size_bytes": 0})

            # Get foreign key relationships
            relationships = await self._get_foreign_keys(table, schema)
            for relationship in relationships:
                all_relationships.append(relationship)

                # Track connections
                from_key = f"{schema}.{table}"
                to_key = f"{relationship['to_schema']}.{relationship['to_table']}"
                table_connections[from_key] = table_connections.get(from_key, 0) + 1  # type: ignore
                table_connections[to_key] = table_connections.get(to_key, 0) + 1  # type: ignore

            if "error" not in table_stats:
                needs_attention = []
                essential_info = {
                    "row_count": table_stats.get("row_count", 0),
                    "size_bytes": table_stats.get("size_bytes", 0),
                    "size_readable": self._format_bytes(
                        table_stats.get("size_bytes", 0)
                    ),
                    "needs_attention": needs_attention,
                }

                # Add performance insights for MySQL
                if table_stats.get("row_count", 0) == 0:
                    needs_attention.append("empty_table")

                # Check for large tables that might need indexing
                if (
                    table_stats.get("size_bytes", 0) > 100 * 1024 * 1024  # > 100MB
                    and table_stats.get("row_count", 0) > 100000
                ):  # > 100k rows
                    needs_attention.append("large_table_review_indexes")

                # Store for analysis
                all_tables_with_stats.append(
                    {
                        "schema": schema,
                        "table": table,
                        "size_bytes": essential_info["size_bytes"],
                        "row_count": essential_info["row_count"],
                    }
                )

                schema_info["tables"][table] = essential_info  # type: ignore
                schema_info["total_size_bytes"] += essential_info["size_bytes"]  # type: ignore
                schema_info["total_rows"] += essential_info["row_count"]  # type: ignore
            else:
                schema_info["tables"][table] = {"error": "stats_unavailable"}  # type: ignore

        return schema_info

    async def _get_tables_in_schema(self, schema: str) -> List[str]:
        """Get list of tables in a schema."""
        query = """
            SELECT TABLE_NAME as table_name
            FROM information_schema.TABLES
            WHERE TABLE_SCHEMA = %s AND TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_NAME
        """
        result = await self.db_manager.execute_query(query.replace("%s", f"'{schema}'"))
        if result.has_results:
            return [dict(zip(result.columns, row))["table_name"] for row in result.rows]
        return []

    async def _get_bulk_table_stats(
        self, tables: List[str], schema: str
    ) -> Dict[str, Dict[str, Any]]:
        """Get table statistics for multiple tables in a single query (no table scans)."""
        if not tables:
            return {}

        try:
            # First, try to update table statistics for better accuracy (non-blocking)
            # ANALYZE TABLE only updates metadata, doesn't scan data
            try:
                for table in tables[:10]:  # Limit to first 10 tables to avoid timeout
                    analyze_query = f"ANALYZE TABLE `{schema}`.`{table}`"
                    await self.db_manager.execute_query(analyze_query)
            except Exception as e:
                logger.debug(f"Could not update table statistics (non-critical): {e}")

            # MySQL table statistics from information_schema (estimates only, no table scans)
            table_list = "', '".join(tables)
            query = f"""
                SELECT
                    TABLE_NAME as table_name,
                    IFNULL(TABLE_ROWS, 0) as row_count,
                    IFNULL(DATA_LENGTH + INDEX_LENGTH, 0) as size_bytes,
                    IFNULL(DATA_LENGTH, 0) as data_size,
                    IFNULL(INDEX_LENGTH, 0) as index_size,
                    IFNULL(AUTO_INCREMENT, 0) as auto_increment,
                    ENGINE as engine
                FROM information_schema.TABLES
                WHERE TABLE_SCHEMA = '{schema}' AND TABLE_NAME IN ('{table_list}')
            """

            result = await self.db_manager.execute_query(query)
            stats_result = {}

            if result.has_results:
                for row in result.rows:
                    row_dict = dict(zip(result.columns, row))
                    table_name = row_dict["table_name"]
                    engine = row_dict.get("engine", "").upper()

                    # Note: TABLE_ROWS is an estimate for InnoDB tables
                    row_count = int(row_dict.get("row_count", 0) or 0)

                    stats_result[table_name] = {
                        "row_count": row_count,
                        "size_bytes": int(row_dict.get("size_bytes", 0) or 0),
                        "data_size": int(row_dict.get("data_size", 0) or 0),
                        "index_size": int(row_dict.get("index_size", 0) or 0),
                        "engine": engine,
                        "is_estimate": engine
                        == "INNODB",  # InnoDB row counts are estimates
                    }

            # Add empty stats for tables not found
            for table in tables:
                if table not in stats_result:
                    stats_result[table] = {
                        "row_count": 0,
                        "size_bytes": 0,
                        "data_size": 0,
                        "index_size": 0,
                        "engine": "UNKNOWN",
                        "is_estimate": True,
                    }

            return stats_result

        except Exception as e:
            logger.warning(f"Could not get bulk stats for schema {schema}: {e}")
            # Fallback to individual queries
            result = {}
            for table in tables:
                result[table] = await self._get_table_stats(table, schema)
            return result

    async def _get_foreign_keys(self, table: str, schema: str) -> List[Dict[str, Any]]:
        """Get foreign key relationships for a table."""
        query = f"""
            SELECT
                tc.CONSTRAINT_NAME as constraint_name,
                tc.TABLE_SCHEMA as from_schema,
                tc.TABLE_NAME as from_table,
                GROUP_CONCAT(kcu.COLUMN_NAME ORDER BY kcu.ORDINAL_POSITION) as from_columns,
                kcu.REFERENCED_TABLE_SCHEMA as to_schema,
                kcu.REFERENCED_TABLE_NAME as to_table,
                GROUP_CONCAT(kcu.REFERENCED_COLUMN_NAME ORDER BY kcu.ORDINAL_POSITION) as to_columns
            FROM information_schema.TABLE_CONSTRAINTS AS tc
            JOIN information_schema.KEY_COLUMN_USAGE AS kcu
                ON tc.CONSTRAINT_NAME = kcu.CONSTRAINT_NAME
                AND tc.TABLE_SCHEMA = kcu.TABLE_SCHEMA
            WHERE tc.CONSTRAINT_TYPE = 'FOREIGN KEY'
                AND tc.TABLE_SCHEMA = '{schema}'
                AND tc.TABLE_NAME = '{table}'
            GROUP BY tc.CONSTRAINT_NAME, tc.TABLE_SCHEMA, tc.TABLE_NAME,
                     kcu.REFERENCED_TABLE_SCHEMA, kcu.REFERENCED_TABLE_NAME
        """

        relationships = []
        try:
            result = await self.db_manager.execute_query(query)
            if result.has_results:
                for row in result.rows:
                    row_dict = dict(zip(result.columns, row))
                    relationship = {
                        "from_schema": row_dict["from_schema"],
                        "from_table": row_dict["from_table"],
                        "from_columns": row_dict["from_columns"].split(",")
                        if row_dict["from_columns"]
                        else [],
                        "to_schema": row_dict["to_schema"],
                        "to_table": row_dict["to_table"],
                        "to_columns": row_dict["to_columns"].split(",")
                        if row_dict["to_columns"]
                        else [],
                        "constraint_name": row_dict["constraint_name"],
                    }
                    relationships.append(relationship)
        except Exception as e:
            logger.warning(f"Could not get foreign keys for {schema}.{table}: {e}")

        return relationships

    async def _get_table_stats(self, table: str, schema: str) -> Dict[str, Any]:
        """Get basic table statistics (no table scans)."""
        try:
            # Try to update table statistics for better accuracy (non-blocking)
            try:
                analyze_query = f"ANALYZE TABLE `{schema}`.`{table}`"
                await self.db_manager.execute_query(analyze_query)
            except Exception as e:
                logger.debug(
                    f"Could not update statistics for {schema}.{table} (non-critical): {e}"
                )

            stats_query = f"""
                SELECT
                    IFNULL(TABLE_ROWS, 0) as row_count,
                    IFNULL(DATA_LENGTH + INDEX_LENGTH, 0) as size_bytes,
                    IFNULL(DATA_LENGTH, 0) as data_size,
                    IFNULL(INDEX_LENGTH, 0) as index_size,
                    ENGINE as engine
                FROM information_schema.TABLES
                WHERE TABLE_SCHEMA = '{schema}' AND TABLE_NAME = '{table}'
            """

            result = await self.db_manager.execute_query(stats_query)
            if result.has_results and result.rows:
                row_dict = dict(zip(result.columns, result.rows[0]))
                engine = row_dict.get("engine", "").upper()
                return {
                    "row_count": int(row_dict.get("row_count", 0) or 0),
                    "size_bytes": int(row_dict.get("size_bytes", 0) or 0),
                    "data_size": int(row_dict.get("data_size", 0) or 0),
                    "index_size": int(row_dict.get("index_size", 0) or 0),
                    "engine": engine,
                    "is_estimate": engine == "INNODB",
                }
            else:
                return {
                    "row_count": 0,
                    "size_bytes": 0,
                    "data_size": 0,
                    "index_size": 0,
                    "engine": "UNKNOWN",
                    "is_estimate": True,
                }
        except Exception as e:
            logger.warning(f"Could not get stats for {schema}.{table}: {e}")
            return {"error": str(e)}

    async def _add_top_tables_summary(
        self, db_info: Dict[str, Any], all_tables_with_stats: List[Dict[str, Any]]
    ) -> None:
        """Add top tables summary for performance insights."""
        # Top 5 tables by size
        top_by_size = sorted(
            all_tables_with_stats, key=lambda x: x["size_bytes"], reverse=True
        )[:5]
        # Top 5 tables by row count
        top_by_rows = sorted(
            all_tables_with_stats, key=lambda x: x["row_count"], reverse=True
        )[:5]

        db_info["performance_overview"]["top_tables"] = {
            "largest": [
                {
                    "schema": t["schema"],
                    "table": t["table"],
                    "size_bytes": t["size_bytes"],
                    "size_readable": self._format_bytes(t["size_bytes"]),
                }
                for t in top_by_size
            ],
            "most_rows": [
                {
                    "schema": t["schema"],
                    "table": t["table"],
                    "row_count": t["row_count"],
                }
                for t in top_by_rows
            ],
        }

    async def _get_security_overview(self, db_info: Dict[str, Any]) -> None:
        """Get security overview and recommendations."""
        security_issues = []
        security_score = 100

        # Check security settings
        security_settings = {}

        try:
            # Check SSL
            ssl_query = "SHOW VARIABLES LIKE 'have_ssl'"
            result = await self.db_manager.execute_query(ssl_query)
            if result.has_results and result.rows:
                ssl_value = dict(zip(result.columns, result.rows[0]))["Value"]
                security_settings["ssl"] = ssl_value
                if ssl_value.lower() != "yes":
                    security_issues.append("ssl_disabled")
                    security_score -= 20

            # Check general log
            log_query = "SHOW VARIABLES LIKE 'general_log'"
            result = await self.db_manager.execute_query(log_query)
            if result.has_results and result.rows:
                log_value = dict(zip(result.columns, result.rows[0]))["Value"]
                security_settings["general_log"] = log_value

            # Check validate_password plugin (MySQL 5.7+)
            try:
                plugin_query = "SHOW PLUGINS"
                result = await self.db_manager.execute_query(plugin_query)
                validate_password_active = False
                if result.has_results:
                    for row in result.rows:
                        row_dict = dict(zip(result.columns, row))
                        if (
                            "validate_password" in row_dict.get("Name", "").lower()
                            and row_dict.get("Status", "").upper() == "ACTIVE"
                        ):
                            validate_password_active = True
                            break
                security_settings["validate_password_plugin"] = validate_password_active
                if not validate_password_active:
                    security_issues.append("no_password_validation")
                    security_score -= 10
            except Exception:
                security_settings["validate_password_plugin"] = "unknown"

        except Exception as e:
            logger.warning(f"Could not check security settings: {e}")

        # Get user security summary
        try:
            users_query = """
                SELECT
                    COUNT(*) as total_users,
                    SUM(CASE WHEN Super_priv = 'Y' THEN 1 ELSE 0 END) as superusers,
                    SUM(CASE WHEN max_connections = 0 THEN 1 ELSE 0 END) as unlimited_connections
                FROM mysql.user
            """

            result = await self.db_manager.execute_query(users_query)
            if result.has_results and result.rows:
                row_dict = dict(zip(result.columns, result.rows[0]))
                total_users = int(row_dict.get("total_users", 0))
                superusers = int(row_dict.get("superusers", 0))
                unlimited_conn = int(row_dict.get("unlimited_connections", 0))

                if superusers > 1:
                    security_issues.append("multiple_superusers")
                    security_score -= 15

                if unlimited_conn > 0:
                    security_issues.append("unlimited_connections")
                    security_score -= 10

                recommendations = []
                if "ssl_disabled" in security_issues:
                    recommendations.append("Enable SSL encryption")
                if "no_password_validation" in security_issues:
                    recommendations.append("Install validate_password plugin")
                if "multiple_superusers" in security_issues:
                    recommendations.append("Review superuser privileges")
                if "unlimited_connections" in security_issues:
                    recommendations.append("Set connection limits for users")

                db_info["security_overview"] = {
                    "security_score": max(0, security_score),
                    "total_users": total_users,
                    "superusers": superusers,
                    "unlimited_connections": unlimited_conn,
                    "security_settings": security_settings,
                    "security_issues": security_issues,
                    "recommendations": recommendations,
                }
        except Exception as e:
            logger.warning(f"Could not get user security info: {e}")
            db_info["security_overview"] = {
                "security_score": security_score,
                "security_settings": security_settings,
                "security_issues": security_issues,
                "recommendations": ["Review security configuration manually"],
            }

    async def _build_relationship_summary(
        self,
        db_info: Dict[str, Any],
        all_relationships: List[Dict[str, Any]],
        table_connections: Dict[str, int],
        user_schemas: List[str],
    ) -> None:
        """Build relationship summary and insights."""
        db_info["relationships"]["foreign_keys"] = all_relationships

        if all_relationships:
            # Find most connected tables
            most_connected = sorted(
                table_connections.items(), key=lambda x: x[1], reverse=True
            )[:5]

            # Find isolated tables
            all_table_keys = set()
            for schema in user_schemas:
                tables = await self._get_tables_in_schema(schema)
                for table in tables:
                    all_table_keys.add(f"{schema}.{table}")

            connected_tables = set(table_connections.keys())
            isolated_tables = all_table_keys - connected_tables

            # Find hub tables (highly referenced)
            relationship_patterns = {}
            for rel in all_relationships:
                to_table = f"{rel['to_schema']}.{rel['to_table']}"
                relationship_patterns[to_table] = (
                    relationship_patterns.get(to_table, 0) + 1  # type: ignore
                )

            hub_tables = sorted(
                relationship_patterns.items(), key=lambda x: x[1], reverse=True
            )[:5]

            insights = []
            if len(isolated_tables) > 0:
                insights.append(
                    f"{len(isolated_tables)} tables have no foreign key relationships"
                )
            if hub_tables:
                top_hub = hub_tables[0]
                insights.append(
                    f"{top_hub[0]} is the most referenced table ({top_hub[1]} references)"
                )

            db_info["relationships"]["relationship_summary"] = {
                "total_relationships": len(all_relationships),
                "connected_tables": len(connected_tables),
                "isolated_tables": len(isolated_tables),
                "most_connected_tables": [
                    {"table": table, "connections": count}
                    for table, count in most_connected
                ],
                "hub_tables": [
                    {"table": table, "referenced_by": count}
                    for table, count in hub_tables
                ],
                "relationship_insights": insights,
            }
        else:
            db_info["relationships"]["relationship_summary"] = {
                "total_relationships": 0,
                "connected_tables": 0,
                "isolated_tables": db_info["database_summary"]["total_tables"],
                "relationship_insights": [
                    "No foreign key relationships found in the database"
                ],
            }

    def _format_bytes(self, bytes_value: int) -> str:
        """Format bytes into human-readable string."""
        if bytes_value == 0:
            return "0 B"

        value = float(bytes_value)
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if value < 1024.0:
                return f"{value:.1f} {unit}"
            value /= 1024.0
        return f"{value:.1f} PB"

    async def _identify_performance_hotspots(
        self, db_info: Dict[str, Any], all_tables_with_stats: List[Dict[str, Any]]
    ) -> None:
        """Identify performance hotspots in the database."""
        try:
            logger.info("Identifying performance hotspots...")

            large_tables = []
            empty_tables = []
            tables_needing_review = []

            hotspots = {
                "large_tables": large_tables,
                "empty_tables": empty_tables,
                "tables_needing_review": tables_needing_review,
                "summary": {
                    "total_hotspots": 0,
                    "critical_issues": 0,
                    "warning_issues": 0,
                },
            }

            for table_info in all_tables_with_stats:
                schema = table_info["schema"]
                table = table_info["table"]
                size_bytes = table_info.get("size_bytes", 0)
                row_count = table_info.get("row_count", 0)
                size_mb = size_bytes / (1024 * 1024)

                # Identify large tables (>1GB)
                if size_mb > 1024:  # > 1GB
                    large_tables.append(
                        {
                            "qualified_name": f"{schema}.{table}",
                            "size_mb": round(size_mb, 2),
                            "row_count": row_count,
                            "severity": "HIGH"
                            if size_mb > 10240
                            else "MEDIUM",  # >10GB = HIGH
                        }
                    )

                # Identify empty tables
                if row_count == 0:
                    empty_tables.append(
                        {
                            "qualified_name": f"{schema}.{table}",
                            "size_mb": round(size_mb, 2),
                        }
                    )

                # Tables that need review (large with potential issues)
                if size_mb > 100:  # >100MB
                    issues = []
                    if row_count == 0:
                        issues.append("Empty table with significant size")
                    elif size_mb / max(row_count, 1) > 1:  # >1MB per 1000 rows
                        issues.append(
                            "High storage per row - check for large TEXT/BLOB columns"
                        )

                    if issues:
                        tables_needing_review.append(
                            {
                                "qualified_name": f"{schema}.{table}",
                                "size_mb": round(size_mb, 2),
                                "row_count": row_count,
                                "issues": issues,
                                "severity": "HIGH" if len(issues) > 1 else "MEDIUM",
                            }
                        )

            # Sort all hotspot lists by severity and size
            for hotspot_type in ["large_tables", "tables_needing_review"]:
                hotspots[hotspot_type] = sorted(
                    hotspots[hotspot_type],
                    key=lambda x: (x["severity"] == "HIGH", x.get("size_mb", 0)),
                    reverse=True,
                )[:10]  # Limit to top 10

            # Calculate summary statistics
            total_hotspots = sum(
                len(hotspots[key]) for key in hotspots if key != "summary"
            )
            critical_issues = sum(
                1
                for hotspot_list in hotspots.values()
                if isinstance(hotspot_list, list)
                for item in hotspot_list
                if item.get("severity") == "HIGH"
            )
            warning_issues = total_hotspots - critical_issues

            hotspots["summary"] = {
                "total_hotspots": total_hotspots,
                "critical_issues": critical_issues,
                "warning_issues": warning_issues,
            }

            db_info["performance_hotspots"] = hotspots
            logger.info(
                f"Performance hotspot analysis complete: {total_hotspots} hotspots identified"
            )

        except Exception as e:
            logger.error(f"Error identifying performance hotspots: {e}")
            db_info["performance_hotspots"] = {
                "error": f"Failed to identify performance hotspots: {str(e)}"
            }

    async def _add_schema_relationship_mapping(
        self, db_info: Dict[str, Any], user_schemas: List[str]
    ) -> None:
        """Add schema relationship mapping analysis to database overview."""
        try:
            logger.info("Analyzing schema relationships...")

            # Perform schema relationship analysis
            schema_mapping_results = (
                await self.schema_mapping_tool.analyze_schema_relationships(
                    user_schemas
                )
            )

            # Add to database info (returns text format)
            db_info["schema_relationship_mapping"] = {
                "analysis_text": schema_mapping_results
            }

            logger.info("Schema relationship mapping complete")

        except Exception as e:
            logger.error(f"Error adding schema relationship mapping: {e}")
            db_info["schema_relationship_mapping"] = {
                "error": f"Failed to analyze schema relationships: {str(e)}"
            }

    def _format_as_text(self, result: Dict[str, Any]) -> str:
        """Format database overview result as agent-readable text."""
        if "error" in result:
            return f"Error: {result['error']}\n\nExecution metadata:\n{self._format_execution_metadata(result.get('execution_metadata', {}))}"

        output = []

        # Database Summary
        output.append("DATABASE OVERVIEW")

        db_summary = result.get("database_summary", {})
        output.append(f"Total Schemas: {db_summary.get('total_schemas', 0)}")
        output.append(f"Total Tables: {db_summary.get('total_tables', 0)}")
        output.append(f"Total Size: {db_summary.get('total_size_readable', 'N/A')}")
        output.append(
            f"Total Rows: {db_summary.get('total_rows', 0):,} (estimates for InnoDB)"
        )
        output.append("")

        # Performance Overview
        perf_overview = result.get("performance_overview", {})
        if perf_overview:
            output.append("PERFORMANCE OVERVIEW")
            output.append(
                f"Active Connections: {perf_overview.get('active_connections', 0)}"
            )
            output.append(f"Max Connections: {perf_overview.get('max_connections', 0)}")
            output.append(
                f"Connection Usage: {perf_overview.get('connection_usage_percent', 0)}%"
            )

            # Top tables
            top_tables = perf_overview.get("top_tables", {})
            if top_tables.get("largest"):
                output.append("\nLargest Tables:")
                for i, table in enumerate(top_tables["largest"], 1):
                    output.append(
                        f"  {i}. {table['schema']}.{table['table']} - {table['size_readable']}"
                    )

            if top_tables.get("most_rows"):
                output.append("\nTables with Most Rows:")
                for i, table in enumerate(top_tables["most_rows"], 1):
                    output.append(
                        f"  {i}. {table['schema']}.{table['table']} - {table['row_count']:,} rows"
                    )
            output.append("")

        # Security Overview
        security_overview = result.get("security_overview", {})
        if security_overview:
            output.append("SECURITY OVERVIEW")
            output.append(
                f"Security Score: {security_overview.get('security_score', 0)}/100"
            )
            output.append(f"Total Users: {security_overview.get('total_users', 0)}")
            output.append(f"Superusers: {security_overview.get('superusers', 0)}")

            security_issues = security_overview.get("security_issues", [])
            if security_issues:
                output.append(f"\nSecurity Issues ({len(security_issues)}):")
                for issue in security_issues:
                    output.append(f"  - {issue}")

            recommendations = security_overview.get("recommendations", [])
            if recommendations:
                output.append("\nRecommendations:")
                for rec in recommendations:
                    output.append(f"  - {rec}")
            output.append("")

        # Performance Hotspots
        hotspots = result.get("performance_hotspots", {})
        if hotspots and "error" not in hotspots:
            summary = hotspots.get("summary", {})
            output.append("PERFORMANCE HOTSPOTS")
            output.append(f"Total Hotspots: {summary.get('total_hotspots', 0)}")
            output.append(f"Critical Issues: {summary.get('critical_issues', 0)}")
            output.append(f"Warning Issues: {summary.get('warning_issues', 0)}")

            # Large tables
            if hotspots.get("large_tables"):
                output.append("\nLarge Tables:")
                for table in hotspots["large_tables"][:5]:
                    output.append(
                        f"  - {table['qualified_name']} - {table['size_mb']} MB ({table['severity']})"
                    )

            # Empty tables
            if hotspots.get("empty_tables"):
                output.append("\nEmpty Tables:")
                for table in hotspots["empty_tables"][:5]:
                    output.append(f"  - {table['qualified_name']}")

            # Tables needing review
            if hotspots.get("tables_needing_review"):
                output.append("\nTables Needing Review:")
                for table in hotspots["tables_needing_review"][:5]:
                    issues = ", ".join(table["issues"])
                    output.append(
                        f"  - {table['qualified_name']} - {issues} ({table['severity']})"
                    )
            output.append("")

        # Relationships Summary
        relationships = result.get("relationships", {})
        if relationships:
            rel_summary = relationships.get("relationship_summary", {})
            output.append("RELATIONSHIPS SUMMARY")
            output.append(
                f"Total Relationships: {rel_summary.get('total_relationships', 0)}"
            )
            output.append(f"Connected Tables: {rel_summary.get('connected_tables', 0)}")
            output.append(f"Isolated Tables: {rel_summary.get('isolated_tables', 0)}")

            # Most connected tables
            most_connected = rel_summary.get("most_connected_tables", [])
            if most_connected:
                output.append("\nMost Connected Tables:")
                for table in most_connected[:5]:
                    output.append(
                        f"  - {table['table']} - {table['connections']} connections"
                    )

            # Hub tables
            hub_tables = rel_summary.get("hub_tables", [])
            if hub_tables:
                output.append("\nHub Tables (Most Referenced):")
                for table in hub_tables[:5]:
                    output.append(
                        f"  - {table['table']} - referenced by {table['referenced_by']} tables"
                    )

            # Insights
            insights = rel_summary.get("relationship_insights", [])
            if insights:
                output.append("\nRelationship Insights:")
                for insight in insights:
                    output.append(f"  - {insight}")
            output.append("")

        # Schema Details
        schemas = result.get("schemas", {})
        if schemas:
            output.append("SCHEMA DETAILS")
            for schema_name, schema_info in schemas.items():
                output.append(f"\n{schema_name}:")
                output.append(f"  Tables: {schema_info.get('table_count', 0)}")
                output.append(
                    f"  Size: {self._format_bytes(schema_info.get('total_size_bytes', 0))}"
                )
                output.append(f"  Rows: {schema_info.get('total_rows', 0):,}")

                if schema_info.get("is_sampled"):
                    output.append(
                        f"  Sampled: {schema_info.get('tables_analyzed', 0)}/{schema_info.get('table_count', 0)} tables analyzed"
                    )

                # Show top tables in schema
                tables = schema_info.get("tables", {})
                if tables:
                    top_schema_tables = sorted(
                        [
                            (name, info)
                            for name, info in tables.items()
                            if "size_bytes" in info
                        ],
                        key=lambda x: x[1]["size_bytes"],
                        reverse=True,
                    )[:3]

                    if top_schema_tables:
                        output.append("  Top tables:")
                        for table_name, table_info in top_schema_tables:
                            output.append(
                                f"    - {table_name} - {table_info.get('size_readable', 'N/A')}"
                            )

        # Schema Relationship Mapping
        schema_mapping = result.get("schema_relationship_mapping", {})
        if schema_mapping:
            output.append("\nSCHEMA RELATIONSHIP MAPPING")

            if "error" in schema_mapping:
                output.append(f"Error: {schema_mapping['error']}")
            elif "analysis_text" in schema_mapping:
                # Add the full schema analysis text
                output.append(schema_mapping["analysis_text"])
            output.append("")

        # Execution Metadata
        metadata = result.get("execution_metadata", {})
        if metadata:
            output.append("EXECUTION METADATA")
            output.append(self._format_execution_metadata(metadata))

        return "\n".join(output)

    def _format_execution_metadata(self, metadata: Dict[str, Any]) -> str:
        """Format execution metadata as text."""
        output = []
        output.append(f"Max Tables: {metadata.get('max_tables', 'N/A')}")
        output.append(f"Sampling Mode: {metadata.get('sampling_mode', 'N/A')}")
        output.append(f"Timeout: {metadata.get('timeout', 'N/A')}s")
        output.append(f"Tables Analyzed: {metadata.get('tables_analyzed', 0)}")
        output.append(f"Tables Skipped: {metadata.get('tables_skipped', 0)}")
        output.append(f"Execution Time: {metadata.get('execution_time', 'N/A')}s")
        output.append(
            "Note: Uses ANALYZE TABLE for better estimates, no full table scans"
        )
        return "\n".join(output)


async def get_database_overview_tool(
    db_manager,
    security_validator,
    max_tables: int = 500,
    sampling_mode: bool = True,
    timeout: int = 300,
) -> str:
    """Get comprehensive database overview with performance and security analysis.

    Args:
        db_manager: Database manager instance
        security_validator: Security validator instance
        max_tables: Maximum number of tables to analyze per schema (default: 500)
        sampling_mode: Use statistical sampling for large datasets (default: True)
        timeout: Maximum execution time in seconds (default: 300)
    """
    try:
        logger.info("Starting database overview analysis...")

        if not db_manager:
            raise RuntimeError("Database manager not initialized")

        overview_tool = DatabaseOverviewTool(db_manager)
        result = await overview_tool.get_database_overview(
            max_tables, sampling_mode, timeout
        )

        logger.info("Database overview analysis completed successfully")
        return result

    except Exception as e:
        logger.error(f"Database overview error: {e}")
        return f"Error generating database overview: {str(e)}"
