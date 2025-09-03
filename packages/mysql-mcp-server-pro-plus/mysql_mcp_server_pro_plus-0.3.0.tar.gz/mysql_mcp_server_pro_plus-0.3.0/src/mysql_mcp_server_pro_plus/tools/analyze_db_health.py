"""Database health analysis tool for comprehensive MySQL database monitoring.

Provides enterprise-grade health checks covering indexes, connections, replication,
buffer cache, constraints, and auto-increment sequences.
"""

from __future__ import annotations

import asyncio
import time
from datetime import datetime
from typing import Any, Dict

try:
    import psutil

    HAS_PSUTIL = True
except ImportError:
    psutil = None
    HAS_PSUTIL = False

from ..logger import logger


class DatabaseHealthAnalyzer:
    """Comprehensive MySQL database health analyzer."""

    def __init__(self, db_manager):
        self.db_manager = db_manager

    async def analyze_db_health(self, timeout: int = 300) -> str:
        """
        Perform comprehensive database health analysis covering:
        - Index health and usage statistics
        - Connection pool status and limits
        - Replication status and lag
        - Buffer pool efficiency
        - Constraint integrity
        - Auto-increment sequence analysis
        - Table fragmentation
        - Performance metrics

        Args:
            timeout: Maximum execution time in seconds (default: 300)

        Returns:
            String containing comprehensive health analysis and recommendations
        """
        start_time = time.time()
        try:
            # Add timeout wrapper
            result = await asyncio.wait_for(
                self._analyze_db_health_internal(start_time),
                timeout=timeout,
            )
            return self._format_as_text(result)
        except asyncio.TimeoutError:
            logger.warning(
                f"Database health analysis timed out after {timeout} seconds"
            )
            return self._format_timeout_result(timeout)
        except Exception as e:
            logger.error(f"Error analyzing database health: {e}")
            return self._format_error_result(str(e))

    async def _analyze_db_health_internal(self, start_time: float) -> Dict[str, Any]:
        """Internal method to perform the actual health analysis."""
        result: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "analysis_duration_seconds": 0.0,
            "health_score": 0.0,
            "critical_issues": [],
            "warnings": [],
            "recommendations": [],
            "sections": {},
        }

        try:
            # 1. Connection Health Analysis
            result["sections"]["connections"] = await self._analyze_connections()

            # 2. Index Health Analysis
            result["sections"]["indexes"] = await self._analyze_indexes()

            # 3. Buffer Pool Analysis
            result["sections"]["buffer_pool"] = await self._analyze_buffer_pool()

            # 4. Replication Health
            result["sections"]["replication"] = await self._analyze_replication()

            # 5. Constraint Integrity
            result["sections"]["constraints"] = await self._analyze_constraints()

            # 6. Auto-increment Analysis
            result["sections"]["auto_increment"] = await self._analyze_auto_increment()

            # 7. Table Fragmentation
            result["sections"]["fragmentation"] = await self._analyze_fragmentation()

            # 8. Performance Metrics
            result["sections"][
                "performance"
            ] = await self._analyze_performance_metrics()

            # 9. Storage Engine Health
            result["sections"][
                "storage_engines"
            ] = await self._analyze_storage_engines()

            # 10. Security Analysis
            result["sections"]["security"] = await self._analyze_security()

            # Calculate overall health score and compile issues
            result = await self._calculate_health_score(result)

            result["analysis_duration_seconds"] = time.time() - start_time

        except Exception as e:
            logger.error(f"Error in health analysis: {e}")
            result["error"] = str(e)
            result["analysis_duration_seconds"] = time.time() - start_time

        return result

    async def _analyze_connections(self) -> Dict[str, Any]:
        """Analyze connection pool health and limits."""
        connections_data: Dict[str, Any] = {
            "status": "healthy",
            "current_connections": 0,
            "max_connections": 0,
            "connection_usage_percent": 0.0,
            "aborted_connections": 0,
            "thread_cache_efficiency": 0.0,
            "details": {},
            "issues": [],
            "recommendations": [],
        }

        try:
            # Get connection statistics
            connection_stats_query = """
            SELECT
                VARIABLE_NAME,
                VARIABLE_VALUE
            FROM performance_schema.global_status
            WHERE VARIABLE_NAME IN (
                'Threads_connected',
                'Threads_running',
                'Threads_created',
                'Threads_cached',
                'Aborted_connections',
                'Aborted_clients',
                'Connection_errors_max_connections',
                'Max_used_connections'
            )
            """

            connection_vars_query = """
            SELECT
                VARIABLE_NAME,
                VARIABLE_VALUE
            FROM performance_schema.global_variables
            WHERE VARIABLE_NAME IN (
                'max_connections',
                'thread_cache_size',
                'connect_timeout',
                'wait_timeout',
                'interactive_timeout'
            )
            """

            stats_result = await self.db_manager.execute_query(connection_stats_query)
            vars_result = await self.db_manager.execute_query(connection_vars_query)

            # Process statistics - handle both list and tuple results
            stats = {}
            if stats_result and isinstance(stats_result, list):
                for row in stats_result:
                    if isinstance(row, (list, tuple)) and len(row) >= 2:
                        try:
                            stats[row[0]] = int(row[1])
                        except (ValueError, TypeError):
                            stats[row[0]] = 0

            variables = {}
            if vars_result and isinstance(vars_result, list):
                for row in vars_result:
                    if isinstance(row, (list, tuple)) and len(row) >= 2:
                        try:
                            variables[row[0]] = int(row[1])
                        except (ValueError, TypeError):
                            variables[row[0]] = 0

            connections_data["current_connections"] = stats.get("Threads_connected", 0)
            connections_data["max_connections"] = variables.get("max_connections", 0)
            connections_data["aborted_connections"] = stats.get(
                "Aborted_connections", 0
            )

            # Calculate connection usage percentage
            if connections_data["max_connections"] > 0:
                connections_data["connection_usage_percent"] = round(
                    (
                        connections_data["current_connections"]
                        / connections_data["max_connections"]
                    )
                    * 100,
                    2,
                )

            # Calculate thread cache efficiency
            threads_created = stats.get("Threads_created", 0)
            threads_connected = stats.get("Threads_connected", 0)
            if threads_created > 0:
                connections_data["thread_cache_efficiency"] = round(
                    ((threads_connected - threads_created) / threads_connected) * 100, 2
                )

            connections_data["details"] = {
                "threads_running": stats.get("Threads_running", 0),
                "threads_cached": stats.get("Threads_cached", 0),
                "threads_created": threads_created,
                "aborted_clients": stats.get("Aborted_clients", 0),
                "connection_errors_max_connections": stats.get(
                    "Connection_errors_max_connections", 0
                ),
                "max_used_connections": stats.get("Max_used_connections", 0),
                "thread_cache_size": variables.get("thread_cache_size", 0),
                "connect_timeout": variables.get("connect_timeout", 0),
                "wait_timeout": variables.get("wait_timeout", 0),
                "interactive_timeout": variables.get("interactive_timeout", 0),
            }

            # Analyze connection health
            if connections_data["connection_usage_percent"] > 80:
                connections_data["status"] = "critical"
                connections_data["issues"].append("🚨 Connection usage above 80%")
                connections_data["recommendations"].append(
                    "Consider increasing max_connections or optimizing connection pooling"
                )
            elif connections_data["connection_usage_percent"] > 60:
                connections_data["status"] = "warning"
                connections_data["issues"].append("⚠️ Connection usage above 60%")

            if connections_data["aborted_connections"] > 100:
                connections_data["issues"].append(
                    "⚠️ High number of aborted connections"
                )
                connections_data["recommendations"].append(
                    "Check for network issues or client timeout configurations"
                )

            if connections_data["thread_cache_efficiency"] < 80:
                connections_data["issues"].append("💡 Low thread cache efficiency")
                connections_data["recommendations"].append(
                    "Consider increasing thread_cache_size"
                )

        except Exception as e:
            logger.error(f"Error analyzing connections: {e}")
            connections_data["error"] = str(e)
            connections_data["status"] = "error"

        return connections_data

    async def _analyze_indexes(self) -> Dict[str, Any]:
        """Analyze index health and usage statistics."""
        indexes_data: Dict[str, Any] = {
            "status": "healthy",
            "total_indexes": 0,
            "unused_indexes": [],
            "duplicate_indexes": [],
            "missing_indexes": [],
            "index_efficiency": 0.0,
            "details": {},
            "issues": [],
            "recommendations": [],
        }

        try:
            # Get index usage statistics
            index_usage_query = """
            SELECT
                OBJECT_SCHEMA as database_name,
                OBJECT_NAME as table_name,
                INDEX_NAME,
                COUNT_FETCH,
                COUNT_INSERT,
                COUNT_UPDATE,
                COUNT_DELETE
            FROM performance_schema.table_io_waits_summary_by_index_usage
            WHERE OBJECT_SCHEMA NOT IN ('mysql', 'information_schema', 'performance_schema', 'sys')
            ORDER BY COUNT_FETCH DESC
            """

            # Get index information
            index_info_query = """
            SELECT
                TABLE_SCHEMA as database_name,
                TABLE_NAME,
                INDEX_NAME,
                NON_UNIQUE,
                COLUMN_NAME,
                CARDINALITY,
                INDEX_TYPE
            FROM information_schema.STATISTICS
            WHERE TABLE_SCHEMA NOT IN ('mysql', 'information_schema', 'performance_schema', 'sys')
            ORDER BY TABLE_SCHEMA, TABLE_NAME, INDEX_NAME, SEQ_IN_INDEX
            """

            # Get table sizes for context
            table_size_query = """
            SELECT
                TABLE_SCHEMA as database_name,
                TABLE_NAME,
                TABLE_ROWS,
                DATA_LENGTH,
                INDEX_LENGTH
            FROM information_schema.TABLES
            WHERE TABLE_SCHEMA NOT IN ('mysql', 'information_schema', 'performance_schema', 'sys')
                AND TABLE_TYPE = 'BASE TABLE'
            """

            usage_result = await self.db_manager.execute_query(index_usage_query)
            info_result = await self.db_manager.execute_query(index_info_query)
            size_result = await self.db_manager.execute_query(table_size_query)

            # Process index usage data
            index_usage = {}
            total_fetches = 0
            for row in usage_result:
                key = f"{row[0]}.{row[1]}.{row[2]}"
                fetches = int(row[3]) if row[3] else 0
                index_usage[key] = {
                    "fetches": fetches,
                    "inserts": int(row[4]) if row[4] else 0,
                    "updates": int(row[5]) if row[5] else 0,
                    "deletes": int(row[6]) if row[6] else 0,
                }
                total_fetches += fetches

            # Process index information
            indexes_info = {}
            for row in info_result:
                key = f"{row[0]}.{row[1]}.{row[2]}"
                if key not in indexes_info:
                    indexes_info[key] = {
                        "database": row[0],
                        "table": row[1],
                        "index_name": row[2],
                        "non_unique": row[3],
                        "columns": [],
                        "cardinality": int(row[5]) if row[5] else 0,
                        "index_type": row[6],
                    }
                indexes_info[key]["columns"].append(row[4])

            # Process table sizes
            table_sizes = {}
            for row in size_result:
                key = f"{row[0]}.{row[1]}"
                table_sizes[key] = {
                    "rows": int(row[2]) if row[2] else 0,
                    "data_length": int(row[3]) if row[3] else 0,
                    "index_length": int(row[4]) if row[4] else 0,
                }

            indexes_data["total_indexes"] = len(indexes_info)

            # Find unused indexes (no fetches)
            for key, info in indexes_info.items():
                usage = index_usage.get(key, {"fetches": 0})
                if usage["fetches"] == 0 and info["index_name"] != "PRIMARY":
                    indexes_data["unused_indexes"].append(
                        {
                            "database": info["database"],
                            "table": info["table"],
                            "index_name": info["index_name"],
                            "columns": info["columns"],
                        }
                    )

            # Find potential duplicate indexes
            index_by_table = {}
            for key, info in indexes_info.items():
                table_key = f"{info['database']}.{info['table']}"
                if table_key not in index_by_table:
                    index_by_table[table_key] = []
                index_by_table[table_key].append(info)

            for table_key, table_indexes in index_by_table.items():
                for i, idx1 in enumerate(table_indexes):
                    for idx2 in table_indexes[i + 1 :]:
                        if (
                            idx1["columns"][: len(idx2["columns"])] == idx2["columns"]
                            or idx2["columns"][: len(idx1["columns"])]
                            == idx1["columns"]
                        ):
                            indexes_data["duplicate_indexes"].append(
                                {
                                    "table": table_key,
                                    "index1": {
                                        "name": idx1["index_name"],
                                        "columns": idx1["columns"],
                                    },
                                    "index2": {
                                        "name": idx2["index_name"],
                                        "columns": idx2["columns"],
                                    },
                                }
                            )

            # Calculate index efficiency
            if total_fetches > 0 and indexes_data["total_indexes"] > 0:
                used_indexes = indexes_data["total_indexes"] - len(
                    indexes_data["unused_indexes"]
                )
                indexes_data["index_efficiency"] = round(
                    (used_indexes / indexes_data["total_indexes"]) * 100, 2
                )

            indexes_data["details"] = {
                "total_index_fetches": total_fetches,
                "used_indexes": indexes_data["total_indexes"]
                - len(indexes_data["unused_indexes"]),
                "table_count": len(table_sizes),
            }

            # Generate recommendations
            if len(indexes_data["unused_indexes"]) > 0:
                indexes_data["status"] = "warning"
                indexes_data["issues"].append(
                    f"💡 {len(indexes_data['unused_indexes'])} unused indexes found"
                )
                indexes_data["recommendations"].append(
                    "Consider removing unused indexes to improve write performance"
                )

            if len(indexes_data["duplicate_indexes"]) > 0:
                indexes_data["issues"].append(
                    f"⚠️ {len(indexes_data['duplicate_indexes'])} potential duplicate indexes"
                )
                indexes_data["recommendations"].append(
                    "Review and consolidate duplicate indexes"
                )

            if indexes_data["index_efficiency"] < 70:
                indexes_data["status"] = "warning"
                indexes_data["issues"].append("⚠️ Low index efficiency")

        except Exception as e:
            logger.error(f"Error analyzing indexes: {e}")
            indexes_data["error"] = str(e)
            indexes_data["status"] = "error"

        return indexes_data

    async def _analyze_buffer_pool(self) -> Dict[str, Any]:
        """Analyze InnoDB buffer pool efficiency."""
        buffer_pool_data: Dict[str, Any] = {
            "status": "healthy",
            "buffer_pool_size": 0,
            "buffer_pool_usage_percent": 0.0,
            "hit_ratio": 0.0,
            "pages_data": 0,
            "pages_free": 0,
            "pages_dirty": 0,
            "details": {},
            "issues": [],
            "recommendations": [],
        }

        try:
            # Get buffer pool statistics
            buffer_pool_query = """
            SELECT
                VARIABLE_NAME,
                VARIABLE_VALUE
            FROM performance_schema.global_status
            WHERE VARIABLE_NAME IN (
                'Innodb_buffer_pool_size',
                'Innodb_buffer_pool_pages_total',
                'Innodb_buffer_pool_pages_data',
                'Innodb_buffer_pool_pages_free',
                'Innodb_buffer_pool_pages_dirty',
                'Innodb_buffer_pool_read_requests',
                'Innodb_buffer_pool_reads',
                'Innodb_buffer_pool_bytes_data',
                'Innodb_buffer_pool_bytes_dirty'
            )
            """

            # Get buffer pool configuration
            buffer_pool_vars_query = """
            SELECT
                VARIABLE_NAME,
                VARIABLE_VALUE
            FROM performance_schema.global_variables
            WHERE VARIABLE_NAME IN (
                'innodb_buffer_pool_size',
                'innodb_buffer_pool_instances',
                'innodb_buffer_pool_chunk_size'
            )
            """

            stats_result = await self.db_manager.execute_query(buffer_pool_query)
            vars_result = await self.db_manager.execute_query(buffer_pool_vars_query)

            # Process statistics
            stats = {}
            if stats_result and isinstance(stats_result, list):
                for row in stats_result:
                    if isinstance(row, (list, tuple)) and len(row) >= 2:
                        try:
                            stats[row[0]] = int(row[1])
                        except (ValueError, TypeError):
                            stats[row[0]] = row[1]

            variables = {}
            if vars_result and isinstance(vars_result, list):
                for row in vars_result:
                    if isinstance(row, (list, tuple)) and len(row) >= 2:
                        try:
                            variables[row[0]] = int(row[1])
                        except (ValueError, TypeError):
                            variables[row[0]] = row[1]

            # Calculate buffer pool metrics
            buffer_pool_data["buffer_pool_size"] = variables.get(
                "innodb_buffer_pool_size", 0
            )
            buffer_pool_data["pages_data"] = stats.get(
                "Innodb_buffer_pool_pages_data", 0
            )
            buffer_pool_data["pages_free"] = stats.get(
                "Innodb_buffer_pool_pages_free", 0
            )
            buffer_pool_data["pages_dirty"] = stats.get(
                "Innodb_buffer_pool_pages_dirty", 0
            )

            pages_total = stats.get("Innodb_buffer_pool_pages_total", 0)
            if pages_total > 0:
                buffer_pool_data["buffer_pool_usage_percent"] = round(
                    ((pages_total - buffer_pool_data["pages_free"]) / pages_total)
                    * 100,
                    2,
                )

            # Calculate hit ratio
            read_requests = stats.get("Innodb_buffer_pool_read_requests", 0)
            reads = stats.get("Innodb_buffer_pool_reads", 0)
            if read_requests > 0:
                buffer_pool_data["hit_ratio"] = round(
                    ((read_requests - reads) / read_requests) * 100, 2
                )

            buffer_pool_data["details"] = {
                "pages_total": pages_total,
                "bytes_data": stats.get("Innodb_buffer_pool_bytes_data", 0),
                "bytes_dirty": stats.get("Innodb_buffer_pool_bytes_dirty", 0),
                "read_requests": read_requests,
                "physical_reads": reads,
                "buffer_pool_instances": variables.get(
                    "innodb_buffer_pool_instances", 1
                ),
                "chunk_size": variables.get("innodb_buffer_pool_chunk_size", 0),
            }

            # Analyze buffer pool health
            if buffer_pool_data["hit_ratio"] < 95:
                buffer_pool_data["status"] = "critical"
                buffer_pool_data["issues"].append("🚨 Low buffer pool hit ratio")
                buffer_pool_data["recommendations"].append(
                    "Consider increasing innodb_buffer_pool_size"
                )
            elif buffer_pool_data["hit_ratio"] < 98:
                buffer_pool_data["status"] = "warning"
                buffer_pool_data["issues"].append(
                    "⚠️ Buffer pool hit ratio could be improved"
                )

            if buffer_pool_data["buffer_pool_usage_percent"] > 90:
                buffer_pool_data["issues"].append("⚠️ High buffer pool usage")
                buffer_pool_data["recommendations"].append(
                    "Monitor buffer pool usage and consider increasing size if needed"
                )

            # Check if buffer pool is too small for system memory
            if HAS_PSUTIL and psutil is not None:
                try:
                    total_memory = psutil.virtual_memory().total
                    bp_size = int(buffer_pool_data["buffer_pool_size"])
                    if bp_size > 0 and bp_size < (total_memory * 0.7):
                        buffer_pool_data["issues"].append(
                            "💡 Buffer pool might be undersized"
                        )
                        buffer_pool_data["recommendations"].append(
                            f"Consider increasing buffer pool size (currently {bp_size // (1024**3)}GB, "
                            f"system has {total_memory // (1024**3)}GB)"
                        )
                except Exception as e:
                    logger.debug(f"Error checking system memory: {e}")

        except Exception as e:
            logger.error(f"Error analyzing buffer pool: {e}")
            buffer_pool_data["error"] = str(e)
            buffer_pool_data["status"] = "error"

        return buffer_pool_data

    async def _analyze_replication(self) -> Dict[str, Any]:
        """Analyze replication status and health."""
        replication_data: Dict[str, Any] = {
            "status": "healthy",
            "is_slave": False,
            "is_master": False,
            "slave_lag_seconds": 0,
            "slave_status": {},
            "master_status": {},
            "issues": [],
            "recommendations": [],
        }

        try:
            # Check if this is a slave
            try:
                slave_status_result = await self.db_manager.execute_query(
                    "SHOW SLAVE STATUS"
                )
                if slave_status_result:
                    replication_data["is_slave"] = True
                    # Parse slave status
                    if slave_status_result[0]:  # If there's data
                        columns = [
                            desc[0] for desc in self.db_manager.cursor.description
                        ]
                        slave_status = dict(zip(columns, slave_status_result[0]))
                        replication_data["slave_status"] = slave_status

                        # Check slave lag
                        if slave_status.get("Seconds_Behind_Master") is not None:
                            replication_data["slave_lag_seconds"] = int(
                                slave_status["Seconds_Behind_Master"]
                            )

                        # Check slave health
                        if slave_status.get("Slave_IO_Running") != "Yes":
                            replication_data["status"] = "critical"
                            replication_data["issues"].append(
                                "🚨 Slave IO thread not running"
                            )

                        if slave_status.get("Slave_SQL_Running") != "Yes":
                            replication_data["status"] = "critical"
                            replication_data["issues"].append(
                                "🚨 Slave SQL thread not running"
                            )

                        if replication_data["slave_lag_seconds"] > 60:
                            replication_data["status"] = "warning"
                            replication_data["issues"].append(
                                f"⚠️ Slave lag: {replication_data['slave_lag_seconds']} seconds"
                            )
                            replication_data["recommendations"].append(
                                "Check network connectivity and master load"
                            )

                        if slave_status.get("Last_Error"):
                            replication_data["status"] = "critical"
                            replication_data["issues"].append(
                                f"🚨 Replication error: {slave_status['Last_Error']}"
                            )
            except Exception as e:
                logger.debug(f"No slave status or error checking slave: {e}")

            # Check if this is a master
            try:
                master_status_result = await self.db_manager.execute_query(
                    "SHOW MASTER STATUS"
                )
                if master_status_result and master_status_result[0]:
                    replication_data["is_master"] = True
                    columns = [desc[0] for desc in self.db_manager.cursor.description]
                    replication_data["master_status"] = dict(
                        zip(columns, master_status_result[0])
                    )
            except Exception as e:
                logger.debug(f"No master status or error checking master: {e}")

            # Check binary log configuration if master
            if replication_data["is_master"]:
                try:
                    binlog_vars_query = """
                    SELECT VARIABLE_NAME, VARIABLE_VALUE
                    FROM performance_schema.global_variables
                    WHERE VARIABLE_NAME IN (
                        'log_bin',
                        'sync_binlog',
                        'binlog_format',
                        'expire_logs_days',
                        'binlog_cache_size'
                    )
                    """
                    binlog_result = await self.db_manager.execute_query(
                        binlog_vars_query
                    )
                    binlog_config = {row[0]: row[1] for row in binlog_result}
                    replication_data["master_status"]["binlog_config"] = binlog_config

                    if binlog_config.get("log_bin") != "ON":
                        replication_data["issues"].append(
                            "⚠️ Binary logging is disabled"
                        )

                    if binlog_config.get("sync_binlog") != "1":
                        replication_data["issues"].append(
                            "💡 Consider setting sync_binlog=1 for durability"
                        )
                        replication_data["recommendations"].append(
                            "Set sync_binlog=1 for ACID compliance"
                        )

                except Exception as e:
                    logger.error(f"Error checking binary log config: {e}")

            # If neither master nor slave
            if not replication_data["is_master"] and not replication_data["is_slave"]:
                replication_data["status"] = "not_configured"

        except Exception as e:
            logger.error(f"Error analyzing replication: {e}")
            replication_data["error"] = str(e)
            replication_data["status"] = "error"

        return replication_data

    async def _analyze_constraints(self) -> Dict[str, Any]:
        """Analyze constraint integrity and foreign key health."""
        constraints_data: Dict[str, Any] = {
            "status": "healthy",
            "foreign_keys": [],
            "check_constraints": [],
            "constraint_violations": [],
            "orphaned_records": [],
            "issues": [],
            "recommendations": [],
        }

        try:
            # Get foreign key constraints
            fk_query = """
            SELECT
                kcu.CONSTRAINT_SCHEMA,
                kcu.CONSTRAINT_NAME,
                kcu.TABLE_NAME,
                kcu.COLUMN_NAME,
                kcu.REFERENCED_TABLE_SCHEMA,
                kcu.REFERENCED_TABLE_NAME,
                kcu.REFERENCED_COLUMN_NAME,
                rc.UPDATE_RULE,
                rc.DELETE_RULE
            FROM information_schema.KEY_COLUMN_USAGE kcu
            LEFT JOIN information_schema.REFERENTIAL_CONSTRAINTS rc
                ON kcu.CONSTRAINT_SCHEMA = rc.CONSTRAINT_SCHEMA
                AND kcu.CONSTRAINT_NAME = rc.CONSTRAINT_NAME
            WHERE kcu.REFERENCED_TABLE_NAME IS NOT NULL
                AND kcu.CONSTRAINT_SCHEMA NOT IN ('mysql', 'information_schema', 'performance_schema', 'sys')
            ORDER BY kcu.CONSTRAINT_SCHEMA, kcu.TABLE_NAME, kcu.CONSTRAINT_NAME
            """

            # Get check constraints (MySQL 8.0+)
            check_constraints_query = """
            SELECT
                CONSTRAINT_SCHEMA,
                CONSTRAINT_NAME,
                TABLE_NAME,
                CHECK_CLAUSE
            FROM information_schema.CHECK_CONSTRAINTS
            WHERE CONSTRAINT_SCHEMA NOT IN ('mysql', 'information_schema', 'performance_schema', 'sys')
            """

            fk_result = await self.db_manager.execute_query(fk_query)

            # Process foreign keys
            for row in fk_result:
                constraints_data["foreign_keys"].append(
                    {
                        "schema": row[0],
                        "constraint_name": row[1],
                        "table": row[2],
                        "column": row[3],
                        "referenced_schema": row[4],
                        "referenced_table": row[5],
                        "referenced_column": row[6],
                        "update_rule": row[7],
                        "delete_rule": row[8],
                    }
                )

            # Try to get check constraints (MySQL 8.0+ feature)
            try:
                check_result = await self.db_manager.execute_query(
                    check_constraints_query
                )
                for row in check_result:
                    constraints_data["check_constraints"].append(
                        {
                            "schema": row[0],
                            "constraint_name": row[1],
                            "table": row[2],
                            "check_clause": row[3],
                        }
                    )
            except Exception as e:
                logger.debug(
                    f"Check constraints not available (likely MySQL < 8.0): {e}"
                )

            # Check for potential orphaned records (sample check)
            for fk in constraints_data["foreign_keys"][
                :5
            ]:  # Limit to first 5 for performance
                try:
                    orphan_query = f"""
                    SELECT COUNT(*) as orphan_count
                    FROM `{fk["schema"]}`.`{fk["table"]}` child
                    LEFT JOIN `{fk["referenced_schema"]}`.`{fk["referenced_table"]}` parent
                        ON child.`{fk["column"]}` = parent.`{fk["referenced_column"]}`
                    WHERE child.`{fk["column"]}` IS NOT NULL
                        AND parent.`{fk["referenced_column"]}` IS NULL
                    """
                    orphan_result = await self.db_manager.execute_query(orphan_query)
                    orphan_count = orphan_result[0][0] if orphan_result else 0

                    if orphan_count > 0:
                        constraints_data["orphaned_records"].append(
                            {
                                "table": f"{fk['schema']}.{fk['table']}",
                                "column": fk["column"],
                                "referenced_table": f"{fk['referenced_schema']}.{fk['referenced_table']}",
                                "orphan_count": orphan_count,
                            }
                        )
                        constraints_data["issues"].append(
                            f"⚠️ {orphan_count} orphaned records in {fk['schema']}.{fk['table']}"
                        )
                except Exception as e:
                    logger.debug(
                        f"Error checking orphaned records for {fk['constraint_name']}: {e}"
                    )

            # Analyze constraint health
            total_constraints = len(constraints_data["foreign_keys"]) + len(
                constraints_data["check_constraints"]
            )
            if len(constraints_data["orphaned_records"]) > 0:
                constraints_data["status"] = "warning"
                constraints_data["recommendations"].append(
                    "Review and clean up orphaned records to maintain referential integrity"
                )

            if total_constraints == 0:
                constraints_data["status"] = "warning"
                constraints_data["issues"].append("💡 No foreign key constraints found")
                constraints_data["recommendations"].append(
                    "Consider adding foreign key constraints to enforce referential integrity"
                )

        except Exception as e:
            logger.error(f"Error analyzing constraints: {e}")
            constraints_data["error"] = str(e)
            constraints_data["status"] = "error"

        return constraints_data

    async def _analyze_auto_increment(self) -> Dict[str, Any]:
        """Analyze auto-increment sequences and potential exhaustion."""
        auto_increment_data: Dict[str, Any] = {
            "status": "healthy",
            "sequences": [],
            "near_exhaustion": [],
            "issues": [],
            "recommendations": [],
        }

        try:
            # Get auto-increment information
            auto_inc_query = """
            SELECT
                t.TABLE_SCHEMA,
                t.TABLE_NAME,
                c.COLUMN_NAME,
                c.DATA_TYPE,
                c.COLUMN_TYPE,
                t.AUTO_INCREMENT
            FROM information_schema.TABLES t
            JOIN information_schema.COLUMNS c
                ON t.TABLE_SCHEMA = c.TABLE_SCHEMA
                AND t.TABLE_NAME = c.TABLE_NAME
            WHERE c.EXTRA = 'auto_increment'
                AND t.TABLE_SCHEMA NOT IN ('mysql', 'information_schema', 'performance_schema', 'sys')
                AND t.AUTO_INCREMENT IS NOT NULL
            """

            result = await self.db_manager.execute_query(auto_inc_query)

            if result and isinstance(result, list):
                for row in result:
                    if isinstance(row, (list, tuple)) and len(row) >= 6:
                        (
                            schema,
                            table,
                            column,
                            data_type,
                            column_type,
                            auto_inc_value,
                        ) = row

                        # Calculate maximum value based on data type
                        max_value = self._get_max_auto_increment_value(
                            data_type, column_type
                        )

                        # Calculate usage percentage
                        usage_percent = 0
                        if max_value > 0 and auto_inc_value:
                            usage_percent = round(
                                (int(auto_inc_value) / max_value) * 100, 4
                            )

                        sequence_info = {
                            "schema": schema,
                            "table": table,
                            "column": column,
                            "data_type": data_type,
                            "column_type": column_type,
                            "current_value": int(auto_inc_value)
                            if auto_inc_value
                            else 0,
                            "max_value": max_value,
                            "usage_percent": usage_percent,
                        }

                        auto_increment_data["sequences"].append(sequence_info)

                        # Check for near exhaustion
                        if usage_percent > 80:
                            auto_increment_data["near_exhaustion"].append(sequence_info)
                            if usage_percent > 95:
                                auto_increment_data["status"] = "critical"
                                auto_increment_data["issues"].append(
                                    f"🚨 Auto-increment near exhaustion: {schema}.{table}.{column} ({usage_percent}%)"
                                )
                                auto_increment_data["recommendations"].append(
                                    f"Consider changing {schema}.{table}.{column} to BIGINT"
                                )
                            else:
                                auto_increment_data["status"] = "warning"
                                auto_increment_data["issues"].append(
                                    f"⚠️ Auto-increment high usage: {schema}.{table}.{column} ({usage_percent}%)"
                                )

            # Additional recommendations
            if len(auto_increment_data["sequences"]) > 0:
                int_sequences = [
                    s
                    for s in auto_increment_data["sequences"]
                    if "int(" in s["column_type"].lower()
                ]
                if len(int_sequences) > 0:
                    auto_increment_data["recommendations"].append(
                        "Monitor auto-increment usage regularly to prevent exhaustion"
                    )

        except Exception as e:
            logger.error(f"Error analyzing auto-increment: {e}")
            auto_increment_data["error"] = str(e)
            auto_increment_data["status"] = "error"

        return auto_increment_data

    def _get_max_auto_increment_value(self, data_type: str, column_type: str) -> int:
        """Get maximum value for auto-increment based on data type."""
        data_type = data_type.lower()
        column_type = column_type.lower()

        unsigned = "unsigned" in column_type

        if data_type == "tinyint":
            return 255 if unsigned else 127
        elif data_type == "smallint":
            return 65535 if unsigned else 32767
        elif data_type == "mediumint":
            return 16777215 if unsigned else 8388607
        elif data_type == "int":
            return 4294967295 if unsigned else 2147483647
        elif data_type == "bigint":
            return 18446744073709551615 if unsigned else 9223372036854775807
        else:
            return 0  # Unknown type

    async def _analyze_fragmentation(self) -> Dict[str, Any]:
        """Analyze table fragmentation and optimization needs."""
        fragmentation_data: Dict[str, Any] = {
            "status": "healthy",
            "fragmented_tables": [],
            "total_fragmentation_mb": 0.0,
            "optimization_candidates": [],
            "issues": [],
            "recommendations": [],
        }

        try:
            # Get table fragmentation information
            fragmentation_query = """
            SELECT
                TABLE_SCHEMA,
                TABLE_NAME,
                ENGINE,
                COALESCE(TABLE_ROWS, 0) as TABLE_ROWS,
                COALESCE(DATA_LENGTH, 0) as DATA_LENGTH,
                COALESCE(INDEX_LENGTH, 0) as INDEX_LENGTH,
                COALESCE(DATA_FREE, 0) as DATA_FREE,
                CASE
                    WHEN (DATA_LENGTH + INDEX_LENGTH + DATA_FREE) > 0
                    THEN ROUND((DATA_FREE / (DATA_LENGTH + INDEX_LENGTH + DATA_FREE)) * 100, 2)
                    ELSE 0
                END as fragmentation_percent
            FROM information_schema.TABLES
            WHERE TABLE_SCHEMA NOT IN ('mysql', 'information_schema', 'performance_schema', 'sys')
                AND TABLE_TYPE = 'BASE TABLE'
                AND ENGINE = 'InnoDB'
                AND DATA_FREE > 0
            ORDER BY DATA_FREE DESC
            """

            result = await self.db_manager.execute_query(fragmentation_query)

            total_fragmentation_bytes = 0
            if result and isinstance(result, list):
                for row in result:
                    if isinstance(row, (list, tuple)) and len(row) >= 8:
                        (
                            schema,
                            table,
                            engine,
                            table_rows,
                            data_length,
                            index_length,
                            data_free,
                            frag_percent,
                        ) = row
                    else:
                        continue

                    data_free_mb = int(data_free) / (1024 * 1024) if data_free else 0
                    total_fragmentation_bytes += int(data_free) if data_free else 0

                    fragmentation_info = {
                        "schema": schema,
                        "table": table,
                        "engine": engine,
                        "rows": int(table_rows) if table_rows else 0,
                        "data_length_mb": int(data_length) / (1024 * 1024)
                        if data_length
                        else 0,
                        "index_length_mb": int(index_length) / (1024 * 1024)
                        if index_length
                        else 0,
                        "data_free_mb": data_free_mb,
                        "fragmentation_percent": float(frag_percent)
                        if frag_percent
                        else 0,
                    }

                    fragmentation_data["fragmented_tables"].append(fragmentation_info)

                    # Identify optimization candidates
                    if (
                        fragmentation_info["fragmentation_percent"] > 10
                        and data_free_mb > 100
                    ):
                        fragmentation_data["optimization_candidates"].append(
                            fragmentation_info
                        )

                        if fragmentation_info["fragmentation_percent"] > 25:
                            fragmentation_data["status"] = "warning"
                            fragmentation_data["issues"].append(
                                f"⚠️ High fragmentation: {schema}.{table} ({frag_percent}%)"
                            )

            fragmentation_data["total_fragmentation_mb"] = round(
                total_fragmentation_bytes / (1024 * 1024), 2
            )

            # Generate recommendations
            if len(fragmentation_data["optimization_candidates"]) > 0:
                fragmentation_data["recommendations"].append(
                    f"Consider running OPTIMIZE TABLE on {len(fragmentation_data['optimization_candidates'])} fragmented tables"
                )

                # Suggest specific tables for optimization
                top_candidates = sorted(
                    fragmentation_data["optimization_candidates"],
                    key=lambda x: x["data_free_mb"],
                    reverse=True,
                )[:3]

                for candidate in top_candidates:
                    fragmentation_data["recommendations"].append(
                        f"OPTIMIZE TABLE `{candidate['schema']}`.`{candidate['table']}` "
                        f"(saves ~{candidate['data_free_mb']:.1f}MB)"
                    )

            if fragmentation_data["total_fragmentation_mb"] > 1000:  # 1GB
                fragmentation_data["status"] = "warning"
                fragmentation_data["issues"].append(
                    f"💡 Total fragmentation: {fragmentation_data['total_fragmentation_mb']:.1f}MB"
                )

        except Exception as e:
            logger.error(f"Error analyzing fragmentation: {e}")
            fragmentation_data["error"] = str(e)
            fragmentation_data["status"] = "error"

        return fragmentation_data

    async def _analyze_performance_metrics(self) -> Dict[str, Any]:
        """Analyze key performance metrics."""
        performance_data: Dict[str, Any] = {
            "status": "healthy",
            "query_cache": {},
            "slow_queries": {},
            "table_locks": {},
            "temporary_tables": {},
            "key_efficiency": {},
            "issues": [],
            "recommendations": [],
        }

        try:
            # Get performance-related status variables
            perf_query = """
            SELECT
                VARIABLE_NAME,
                VARIABLE_VALUE
            FROM performance_schema.global_status
            WHERE VARIABLE_NAME IN (
                'Qcache_hits',
                'Qcache_inserts',
                'Qcache_not_cached',
                'Slow_queries',
                'Questions',
                'Uptime',
                'Table_locks_immediate',
                'Table_locks_waited',
                'Created_tmp_tables',
                'Created_tmp_disk_tables',
                'Key_read_requests',
                'Key_reads',
                'Sort_merge_passes',
                'Sort_range',
                'Sort_scan'
            )
            """

            result = await self.db_manager.execute_query(perf_query)
            stats = {}
            if result and isinstance(result, list):
                for row in result:
                    if isinstance(row, (list, tuple)) and len(row) >= 2:
                        try:
                            stats[row[0]] = int(row[1])
                        except (ValueError, TypeError):
                            stats[row[0]] = 0

            # Analyze query cache (if enabled)
            qcache_hits = stats.get("Qcache_hits", 0)
            qcache_inserts = stats.get("Qcache_inserts", 0)
            qcache_not_cached = stats.get("Qcache_not_cached", 0)

            if qcache_hits + qcache_inserts > 0:
                performance_data["query_cache"] = {
                    "hits": qcache_hits,
                    "inserts": qcache_inserts,
                    "not_cached": qcache_not_cached,
                    "hit_ratio": round(
                        (qcache_hits / (qcache_hits + qcache_inserts)) * 100, 2
                    ),
                }

                if performance_data["query_cache"]["hit_ratio"] < 80:
                    performance_data["issues"].append("💡 Low query cache hit ratio")
                    performance_data["recommendations"].append(
                        "Review query cache configuration"
                    )

            # Analyze slow queries
            slow_queries = stats.get("Slow_queries", 0)
            questions = stats.get("Questions", 0)
            uptime = stats.get("Uptime", 1)

            performance_data["slow_queries"] = {
                "total": slow_queries,
                "per_second": round(slow_queries / uptime, 4) if uptime > 0 else 0,
                "percentage": round((slow_queries / questions) * 100, 4)
                if questions > 0
                else 0,
            }

            if performance_data["slow_queries"]["percentage"] > 5:
                performance_data["status"] = "warning"
                performance_data["issues"].append("⚠️ High percentage of slow queries")
                performance_data["recommendations"].append(
                    "Enable slow query log and analyze slow queries"
                )

            # Analyze table locks
            table_locks_immediate = stats.get("Table_locks_immediate", 0)
            table_locks_waited = stats.get("Table_locks_waited", 0)

            if table_locks_immediate + table_locks_waited > 0:
                lock_contention = round(
                    (table_locks_waited / (table_locks_immediate + table_locks_waited))
                    * 100,
                    2,
                )
                performance_data["table_locks"] = {
                    "immediate": table_locks_immediate,
                    "waited": table_locks_waited,
                    "contention_percent": lock_contention,
                }

                if lock_contention > 1:
                    performance_data["issues"].append(
                        f"⚠️ Table lock contention: {lock_contention}%"
                    )
                    performance_data["recommendations"].append(
                        "Consider using InnoDB instead of MyISAM"
                    )

            # Analyze temporary tables
            tmp_tables = stats.get("Created_tmp_tables", 0)
            tmp_disk_tables = stats.get("Created_tmp_disk_tables", 0)

            if tmp_tables > 0:
                disk_tmp_ratio = round((tmp_disk_tables / tmp_tables) * 100, 2)
                performance_data["temporary_tables"] = {
                    "created": tmp_tables,
                    "created_on_disk": tmp_disk_tables,
                    "disk_ratio_percent": disk_tmp_ratio,
                }

                if disk_tmp_ratio > 10:
                    performance_data["issues"].append(
                        f"⚠️ High disk temp table ratio: {disk_tmp_ratio}%"
                    )
                    performance_data["recommendations"].append(
                        "Consider increasing tmp_table_size and max_heap_table_size"
                    )

            # Analyze key efficiency
            key_read_requests = stats.get("Key_read_requests", 0)
            key_reads = stats.get("Key_reads", 0)

            if key_read_requests > 0:
                key_hit_ratio = round(
                    ((key_read_requests - key_reads) / key_read_requests) * 100, 2
                )
                performance_data["key_efficiency"] = {
                    "read_requests": key_read_requests,
                    "reads_from_disk": key_reads,
                    "hit_ratio_percent": key_hit_ratio,
                }

                if key_hit_ratio < 95:
                    performance_data["issues"].append(
                        f"💡 Low key cache hit ratio: {key_hit_ratio}%"
                    )
                    performance_data["recommendations"].append(
                        "Consider increasing key_buffer_size"
                    )

        except Exception as e:
            logger.error(f"Error analyzing performance metrics: {e}")
            performance_data["error"] = str(e)
            performance_data["status"] = "error"

        return performance_data

    async def _analyze_storage_engines(self) -> Dict[str, Any]:
        """Analyze storage engine usage and health."""
        storage_data: Dict[str, Any] = {
            "status": "healthy",
            "engines": {},
            "table_distribution": {},
            "issues": [],
            "recommendations": [],
        }

        try:
            # Get storage engine information
            engines_query = """
            SELECT
                ENGINE,
                SUPPORT,
                COMMENT
            FROM information_schema.ENGINES
            """

            # Get table distribution by engine
            table_engines_query = """
            SELECT
                COALESCE(ENGINE, 'Unknown') as ENGINE,
                COUNT(*) as table_count,
                ROUND(SUM(COALESCE(DATA_LENGTH, 0) + COALESCE(INDEX_LENGTH, 0)) / 1024 / 1024, 2) as size_mb
            FROM information_schema.TABLES
            WHERE TABLE_SCHEMA NOT IN ('mysql', 'information_schema', 'performance_schema', 'sys')
                AND TABLE_TYPE = 'BASE TABLE'
                AND ENGINE IS NOT NULL
            GROUP BY ENGINE
            ORDER BY table_count DESC
            """

            engines_result = await self.db_manager.execute_query(engines_query)
            tables_result = await self.db_manager.execute_query(table_engines_query)

            # Process available engines
            if engines_result and isinstance(engines_result, list):
                for row in engines_result:
                    if isinstance(row, (list, tuple)) and len(row) >= 3:
                        engine, support, comment = row
                        storage_data["engines"][engine] = {
                            "support": support,
                            "comment": comment,
                        }

            # Process table distribution
            total_tables = 0
            if tables_result and isinstance(tables_result, list):
                for row in tables_result:
                    if isinstance(row, (list, tuple)) and len(row) >= 3:
                        engine, table_count, size_mb = row
                        total_tables += int(table_count)
                        storage_data["table_distribution"][engine] = {
                            "table_count": int(table_count),
                            "size_mb": float(size_mb) if size_mb else 0,
                        }

            # Analyze storage engine health
            myisam_tables = (
                storage_data["table_distribution"]
                .get("MyISAM", {})
                .get("table_count", 0)
            )

            if myisam_tables > 0 and total_tables > 0:
                myisam_percent = round((myisam_tables / total_tables) * 100, 2)
                if myisam_percent > 20:
                    storage_data["status"] = "warning"
                    storage_data["issues"].append(
                        f"⚠️ {myisam_percent}% of tables use MyISAM"
                    )
                    storage_data["recommendations"].append(
                        "Consider migrating MyISAM tables to InnoDB for better performance and ACID compliance"
                    )

            # Check for fragmented storage engines
            memory_tables = (
                storage_data["table_distribution"]
                .get("MEMORY", {})
                .get("table_count", 0)
            )
            if memory_tables > 0:
                storage_data["issues"].append("💡 MEMORY engine tables detected")
                storage_data["recommendations"].append(
                    "Monitor MEMORY tables for data persistence requirements"
                )

            # Check InnoDB availability
            if (
                "InnoDB" not in storage_data["engines"]
                or storage_data["engines"]["InnoDB"]["support"] != "DEFAULT"
            ):
                storage_data["status"] = "warning"
                storage_data["issues"].append(
                    "⚠️ InnoDB is not the default storage engine"
                )
                storage_data["recommendations"].append(
                    "Consider setting InnoDB as default storage engine"
                )

        except Exception as e:
            logger.error(f"Error analyzing storage engines: {e}")
            storage_data["error"] = str(e)
            storage_data["status"] = "error"

        return storage_data

    async def _analyze_security(self) -> Dict[str, Any]:
        """Analyze security-related configuration."""
        security_data: Dict[str, Any] = {
            "status": "healthy",
            "user_accounts": [],
            "privileges": {},
            "ssl_status": {},
            "configuration": {},
            "issues": [],
            "recommendations": [],
        }

        try:
            # Get user account information
            users_query = """
            SELECT
                User,
                Host,
                account_locked,
                password_expired,
                password_lifetime,
                password_last_changed
            FROM mysql.user
            WHERE User != ''
            ORDER BY User, Host
            """

            # Get SSL status
            ssl_query = """
            SELECT
                VARIABLE_NAME,
                VARIABLE_VALUE
            FROM performance_schema.global_variables
            WHERE VARIABLE_NAME IN (
                'have_ssl',
                'ssl_cert',
                'ssl_key',
                'ssl_ca'
            )
            """

            # Get security-related configuration
            security_vars_query = """
            SELECT
                VARIABLE_NAME,
                VARIABLE_VALUE
            FROM performance_schema.global_variables
            WHERE VARIABLE_NAME IN (
                'validate_password_policy',
                'validate_password_length',
                'default_password_lifetime',
                'disconnect_on_expired_password',
                'local_infile',
                'secure_file_priv'
            )
            """

            try:
                users_result = await self.db_manager.execute_query(users_query)
                for row in users_result:
                    user, host, locked, expired, lifetime, last_changed = row
                    security_data["user_accounts"].append(
                        {
                            "user": user,
                            "host": host,
                            "account_locked": locked,
                            "password_expired": expired,
                            "password_lifetime": lifetime,
                            "password_last_changed": last_changed,
                        }
                    )
            except Exception as e:
                logger.debug(f"Could not access mysql.user table: {e}")
                security_data["issues"].append(
                    "💡 Could not analyze user accounts (insufficient privileges)"
                )

            # Check SSL configuration
            ssl_result = await self.db_manager.execute_query(ssl_query)
            for row in ssl_result:
                security_data["ssl_status"][row[0]] = row[1]

            if security_data["ssl_status"].get("have_ssl") != "YES":
                security_data["status"] = "warning"
                security_data["issues"].append("⚠️ SSL is not enabled")
                security_data["recommendations"].append(
                    "Enable SSL for secure connections"
                )

            # Check security configuration
            security_result = await self.db_manager.execute_query(security_vars_query)
            for row in security_result:
                security_data["configuration"][row[0]] = row[1]

            # Analyze security issues
            if security_data["configuration"].get("local_infile") == "ON":
                security_data["issues"].append("⚠️ local_infile is enabled")
                security_data["recommendations"].append(
                    "Consider disabling local_infile for security"
                )

            # Check for users with weak host patterns
            for user_info in security_data["user_accounts"]:
                if user_info["host"] == "%":
                    security_data["issues"].append(
                        f"⚠️ User '{user_info['user']}' allows connections from any host"
                    )
                    security_data["recommendations"].append(
                        f"Restrict host access for user '{user_info['user']}'"
                    )

            # Check for expired passwords
            expired_users = [
                u
                for u in security_data["user_accounts"]
                if u["password_expired"] == "Y"
            ]
            if expired_users:
                security_data["issues"].append(
                    f"⚠️ {len(expired_users)} users have expired passwords"
                )

        except Exception as e:
            logger.error(f"Error analyzing security: {e}")
            security_data["error"] = str(e)
            security_data["status"] = "error"

        return security_data

    async def _calculate_health_score(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall health score and compile issues."""
        critical_issues = []
        warnings = []
        recommendations = []

        section_scores = {}
        total_score = 0
        section_count = 0

        for section_name, section_data in result["sections"].items():
            if isinstance(section_data, dict) and "status" in section_data:
                status = section_data["status"]

                # Calculate section score
                if status == "healthy":
                    score = 100
                elif status == "warning":
                    score = 70
                elif status == "critical":
                    score = 30
                elif status == "not_configured":
                    score = 80  # Not necessarily bad
                else:  # error
                    score = 0

                section_scores[section_name] = score
                total_score += score
                section_count += 1

                # Collect issues and recommendations
                if "issues" in section_data:
                    for issue in section_data["issues"]:
                        if issue.startswith("🚨"):
                            critical_issues.append(f"{section_name}: {issue}")
                        elif issue.startswith("⚠️"):
                            warnings.append(f"{section_name}: {issue}")
                        else:
                            warnings.append(f"{section_name}: {issue}")

                if "recommendations" in section_data:
                    for rec in section_data["recommendations"]:
                        recommendations.append(f"{section_name}: {rec}")

        # Calculate overall health score
        if section_count > 0:
            result["health_score"] = round(total_score / section_count, 2)
        else:
            result["health_score"] = 0

        result["section_scores"] = section_scores
        result["critical_issues"] = critical_issues
        result["warnings"] = warnings
        result["recommendations"] = recommendations

        return result

    def _format_as_text(self, result: Dict[str, Any]) -> str:
        """Format the analysis result as agent-readable text."""
        lines = []

        # Header
        lines.append("MYSQL DATABASE HEALTH ANALYSIS REPORT")
        lines.append(f"Analysis Time: {result['timestamp']}")
        lines.append(f"Duration: {result['analysis_duration_seconds']:.2f} seconds")
        lines.append(f"Overall Health Score: {result['health_score']}/100")
        lines.append("")

        # Health Status Summary
        if result["health_score"] >= 90:
            status_text = "EXCELLENT"
        elif result["health_score"] >= 75:
            status_text = "GOOD"
        elif result["health_score"] >= 60:
            status_text = "FAIR"
        elif result["health_score"] >= 40:
            status_text = "POOR"
        else:
            status_text = "CRITICAL"

        lines.append(f"Overall Status: {status_text}")
        lines.append("")

        # Critical Issues
        if result["critical_issues"]:
            lines.append("CRITICAL ISSUES:")
            for issue in result["critical_issues"]:
                lines.append(f"  - {issue}")
            lines.append("")

        # Warnings
        if result["warnings"]:
            lines.append("WARNINGS:")
            for warning in result["warnings"]:
                lines.append(f"  - {warning}")
            lines.append("")

        # Section Details
        lines.append("DETAILED ANALYSIS:")

        for section_name, section_data in result["sections"].items():
            if not isinstance(section_data, dict):
                continue

            section_title = section_name.replace("_", " ").title()
            score = result["section_scores"].get(section_name, 0)
            status = section_data.get("status", "unknown")

            lines.append(f"\n{section_title} (Score: {score}/100)")

            if status == "error":
                lines.append(f"Error: {section_data.get('error', 'Unknown error')}")
                continue

            # Section-specific formatting
            if section_name == "connections":
                lines.append(
                    f"  Current Connections: {section_data.get('current_connections', 0)}"
                )
                lines.append(
                    f"  Max Connections: {section_data.get('max_connections', 0)}"
                )
                lines.append(
                    f"  Usage: {section_data.get('connection_usage_percent', 0)}%"
                )
                lines.append(
                    f"  Thread Cache Efficiency: {section_data.get('thread_cache_efficiency', 0)}%"
                )
                lines.append(
                    f"  Aborted Connections: {section_data.get('aborted_connections', 0)}"
                )

            elif section_name == "indexes":
                lines.append(f"  Total Indexes: {section_data.get('total_indexes', 0)}")
                lines.append(
                    f"  Unused Indexes: {len(section_data.get('unused_indexes', []))}"
                )
                lines.append(
                    f"  Duplicate Indexes: {len(section_data.get('duplicate_indexes', []))}"
                )
                lines.append(
                    f"  Index Efficiency: {section_data.get('index_efficiency', 0)}%"
                )

            elif section_name == "buffer_pool":
                lines.append(
                    f"  Buffer Pool Size: {section_data.get('buffer_pool_size', 0) // (1024**3)}GB"
                )
                lines.append(
                    f"  Usage: {section_data.get('buffer_pool_usage_percent', 0)}%"
                )
                lines.append(f"  Hit Ratio: {section_data.get('hit_ratio', 0)}%")
                lines.append(f"  Pages Data: {section_data.get('pages_data', 0)}")
                lines.append(f"  Pages Free: {section_data.get('pages_free', 0)}")
                lines.append(f"  Pages Dirty: {section_data.get('pages_dirty', 0)}")

            elif section_name == "replication":
                if section_data.get("is_slave"):
                    lines.append("  Role: Slave")
                    lines.append(
                        f"  Lag: {section_data.get('slave_lag_seconds', 0)} seconds"
                    )
                elif section_data.get("is_master"):
                    lines.append("  Role: Master")
                else:
                    lines.append("  Role: Standalone (no replication)")

            elif section_name == "auto_increment":
                sequences = section_data.get("sequences", [])
                near_exhaustion = section_data.get("near_exhaustion", [])
                lines.append(f"  Auto-increment Sequences: {len(sequences)}")
                lines.append(f"  Near Exhaustion: {len(near_exhaustion)}")
                for seq in near_exhaustion[:3]:  # Show top 3
                    lines.append(
                        f"    - {seq['schema']}.{seq['table']}.{seq['column']}: {seq['usage_percent']}%"
                    )

            elif section_name == "fragmentation":
                lines.append(
                    f"  Total Fragmentation: {section_data.get('total_fragmentation_mb', 0)}MB"
                )
                lines.append(
                    f"  Fragmented Tables: {len(section_data.get('fragmented_tables', []))}"
                )
                lines.append(
                    f"  Optimization Candidates: {len(section_data.get('optimization_candidates', []))}"
                )

        # Recommendations
        if result["recommendations"]:
            lines.append("\nRECOMMENDATIONS:")
            for i, rec in enumerate(
                result["recommendations"][:10], 1
            ):  # Top 10 recommendations
                lines.append(f"{i:2}. {rec}")

        lines.append("\nEnd of Health Analysis Report")

        return "\n".join(lines)

    def _format_timeout_result(self, timeout: int) -> str:
        """Format timeout result."""
        return f"""
MySQL Database Health Analysis - TIMEOUT

Analysis timed out after {timeout} seconds.

This may indicate:
- Database is under heavy load
- Complex queries taking too long
- Network connectivity issues
- Large dataset requiring more time

Recommendations:
- Try again during off-peak hours
- Increase timeout value
- Check database performance
- Review current database load
"""

    def _format_error_result(self, error: str) -> str:
        """Format error result."""
        return f"""
MySQL Database Health Analysis - ERROR

Analysis failed with error: {error}

This may indicate:
- Insufficient database privileges
- Database connectivity issues
- Unsupported MySQL version
- Configuration problems

Recommendations:
- Check database connection
- Verify user privileges
- Review MySQL version compatibility
- Check error logs for details
"""


async def analyze_db_health_tool(db_manager, timeout: int = 300) -> str:
    """
    Analyze comprehensive database health with enterprise-grade checks.

    Args:
        db_manager: Database manager instance
        timeout: Maximum execution time in seconds (default: 300)

    Returns:
        Formatted string containing health analysis results
    """
    analyzer = DatabaseHealthAnalyzer(db_manager)
    return await analyzer.analyze_db_health(timeout)
