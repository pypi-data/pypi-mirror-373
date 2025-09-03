"""Blocking queries analysis tool for MySQL databases.

Provides comprehensive analysis of query locks and blocking relationships using
MySQL's PERFORMANCE_SCHEMA and INFORMATION_SCHEMA.
"""

from __future__ import annotations

import asyncio
import time
from datetime import datetime
from typing import Any, Dict, List

from ..logger import logger


class BlockingQueriesAnalyzer:
    """Analyzer for MySQL blocking queries and lock contention."""

    def __init__(self, db_manager):
        self.db_manager = db_manager

    async def get_blocking_queries(self, timeout: int = 300) -> str:
        """
        Get comprehensive blocking queries analysis using MySQL PERFORMANCE_SCHEMA.
        Enhanced with lock wait graph visualization, deadlock detection, session termination
        recommendations, lock timeout suggestions, and historical analysis.

        Args:
            timeout: Maximum execution time in seconds (default: 300)

        Returns:
            String containing blocking queries data, summary, and recommendations
        """
        start_time = time.time()
        try:
            # Add timeout wrapper
            result = await asyncio.wait_for(
                self._get_blocking_queries_internal(start_time),
                timeout=timeout,
            )
            return self._format_as_text(result)
        except asyncio.TimeoutError:
            logger.warning(
                f"Blocking queries analysis timed out after {timeout} seconds"
            )
            return self._format_timeout_result(timeout)
        except Exception as e:
            logger.error(f"Error analyzing blocking queries: {e}")
            return self._format_error_result(str(e))

    async def _get_blocking_queries_internal(self, start_time: float) -> Dict[str, Any]:
        """Internal method for comprehensive blocking queries analysis."""
        try:
            # Get comprehensive blocking analysis
            blocking_data = await self._get_blocking_data()

            if not blocking_data:
                # Get system information even when no current blocking
                deadlock_info = await self._get_deadlock_analysis()
                lock_contention_hotspots = await self._get_lock_contention_hotspots()

                result = {
                    "status": "healthy",
                    "message": "No blocking queries found - all queries are running without locks.",
                    "blocking_queries": [],
                    "summary": {
                        "total_blocked": 0,
                        "total_blocking": 0,
                        "max_wait_time": 0,
                        "affected_relations": [],
                    },
                    "deadlock_analysis": deadlock_info,
                    "lock_contention_hotspots": lock_contention_hotspots,
                    "recommendations": await self._generate_healthy_recommendations(),
                    "execution_metadata": {
                        "execution_time_seconds": time.time() - start_time,
                        "timestamp": datetime.now().isoformat(),
                    },
                }
                return result

            # Enhanced analysis for blocking queries
            lock_wait_graph = await self._generate_lock_wait_graph(blocking_data)
            deadlock_info = await self._get_deadlock_analysis()
            session_termination_recs = (
                await self._generate_session_termination_recommendations(blocking_data)
            )
            lock_timeout_suggestions = await self._generate_lock_timeout_suggestions(
                blocking_data
            )
            historical_analysis = await self._get_historical_blocking_analysis()
            lock_contention_hotspots = await self._get_lock_contention_hotspots()

            # Process blocking queries data with improved structure
            blocking_pids = set()
            blocked_pids = set()
            relations = set()
            max_wait_time = 0

            for block in blocking_data:
                duration = block["blocked_process"]["duration_seconds"]
                max_wait_time = max(max_wait_time, duration)

                if block["blocking_process"]["thread_id"]:
                    blocking_pids.add(block["blocking_process"]["thread_id"])
                blocked_pids.add(block["blocked_process"]["thread_id"])

                if block["lock_info"]["affected_objects"]:
                    relations.update(block["lock_info"]["affected_objects"].split(", "))

            # Generate enhanced summary
            summary = {
                "total_blocked": len(blocked_pids),
                "total_blocking": len(blocking_pids),
                "max_wait_time_seconds": max_wait_time,
                "affected_relations": list(relations),
                "analysis_timestamp": datetime.now().isoformat(),
                "lock_wait_threshold_alerts": self._check_lock_wait_thresholds(
                    blocking_data
                ),
            }

            recommendations = await self._generate_enhanced_recommendations(
                blocking_data,
                summary,
                session_termination_recs,
                lock_timeout_suggestions,
                historical_analysis,
            )

            result = {
                "status": "blocking_detected",
                "blocking_queries": blocking_data,
                "summary": summary,
                "lock_wait_graph": lock_wait_graph,
                "deadlock_analysis": deadlock_info,
                "session_termination_recommendations": session_termination_recs,
                "lock_timeout_suggestions": lock_timeout_suggestions,
                "historical_analysis": historical_analysis,
                "lock_contention_hotspots": lock_contention_hotspots,
                "recommendations": recommendations,
                "execution_metadata": {
                    "execution_time_seconds": time.time() - start_time,
                    "timestamp": datetime.now().isoformat(),
                },
            }
            return result
        except Exception as e:
            logger.error(f"Error in blocking queries analysis: {e}")
            raise

    async def _get_blocking_data(self) -> List[Dict[str, Any]]:
        """Get comprehensive blocking queries data using MySQL PERFORMANCE_SCHEMA."""
        blocking_query = """
            SELECT 
                -- Blocked process information
                p_blocked.PROCESSLIST_ID as blocked_thread_id,
                p_blocked.PROCESSLIST_USER as blocked_user,
                p_blocked.PROCESSLIST_HOST as blocked_host,
                p_blocked.PROCESSLIST_DB as blocked_db,
                p_blocked.PROCESSLIST_COMMAND as blocked_command,
                p_blocked.PROCESSLIST_STATE as blocked_state,
                p_blocked.PROCESSLIST_INFO as blocked_query,
                p_blocked.PROCESSLIST_TIME as blocked_time_seconds,
                
                -- Blocking process information
                p_blocking.PROCESSLIST_ID as blocking_thread_id,
                p_blocking.PROCESSLIST_USER as blocking_user,
                p_blocking.PROCESSLIST_HOST as blocking_host,
                p_blocking.PROCESSLIST_DB as blocking_db,
                p_blocking.PROCESSLIST_COMMAND as blocking_command,
                p_blocking.PROCESSLIST_STATE as blocking_state,
                p_blocking.PROCESSLIST_INFO as blocking_query,
                p_blocking.PROCESSLIST_TIME as blocking_time_seconds,
                
                -- Lock wait information
                dlw.REQUESTING_ENGINE_LOCK_ID as requesting_lock_id,
                dlw.BLOCKING_ENGINE_LOCK_ID as blocking_lock_id,
                
                -- Lock details
                dl_blocked.LOCK_TYPE as blocked_lock_type,
                dl_blocked.LOCK_MODE as blocked_lock_mode,
                dl_blocked.LOCK_STATUS as blocked_lock_status,
                dl_blocked.LOCK_DATA as blocked_lock_data,
                dl_blocked.OBJECT_SCHEMA as blocked_object_schema,
                dl_blocked.OBJECT_NAME as blocked_object_name,
                
                dl_blocking.LOCK_TYPE as blocking_lock_type,
                dl_blocking.LOCK_MODE as blocking_lock_mode,
                dl_blocking.LOCK_STATUS as blocking_lock_status,
                dl_blocking.LOCK_DATA as blocking_lock_data,
                dl_blocking.OBJECT_SCHEMA as blocking_object_schema,
                dl_blocking.OBJECT_NAME as blocking_object_name
                
            FROM performance_schema.data_lock_waits dlw
            JOIN performance_schema.data_locks dl_blocked 
                ON dlw.REQUESTING_ENGINE_LOCK_ID = dl_blocked.ENGINE_LOCK_ID
            JOIN performance_schema.data_locks dl_blocking 
                ON dlw.BLOCKING_ENGINE_LOCK_ID = dl_blocking.ENGINE_LOCK_ID
            JOIN information_schema.processlist p_blocked 
                ON dl_blocked.ENGINE_TRANSACTION_ID = p_blocked.PROCESSLIST_ID
            JOIN information_schema.processlist p_blocking 
                ON dl_blocking.ENGINE_TRANSACTION_ID = p_blocking.PROCESSLIST_ID
            ORDER BY p_blocked.PROCESSLIST_TIME DESC;
        """

        try:
            result = await self.db_manager.execute_query(blocking_query)
            if not result.has_results or not result.rows:
                return []

            blocking_data = []
            for row in result.rows:
                # Map row data to dictionary using column names
                row_dict = dict(zip(result.columns, row))

                duration = float(row_dict.get("blocked_time_seconds", 0))
                blocking_duration = float(row_dict.get("blocking_time_seconds", 0))

                # Build affected objects string
                affected_objects = []
                if row_dict.get("blocked_object_schema") and row_dict.get(
                    "blocked_object_name"
                ):
                    affected_objects.append(
                        f"{row_dict['blocked_object_schema']}.{row_dict['blocked_object_name']}"
                    )
                if row_dict.get("blocking_object_schema") and row_dict.get(
                    "blocking_object_name"
                ):
                    blocking_obj = f"{row_dict['blocking_object_schema']}.{row_dict['blocking_object_name']}"
                    if blocking_obj not in affected_objects:
                        affected_objects.append(blocking_obj)

                blocking_data.append(
                    {
                        "blocked_process": {
                            "thread_id": row_dict.get("blocked_thread_id"),
                            "user": row_dict.get("blocked_user"),
                            "host": row_dict.get("blocked_host"),
                            "database": row_dict.get("blocked_db"),
                            "command": row_dict.get("blocked_command"),
                            "state": row_dict.get("blocked_state"),
                            "query": row_dict.get("blocked_query"),
                            "duration_seconds": duration,
                        },
                        "blocking_process": {
                            "thread_id": row_dict.get("blocking_thread_id"),
                            "user": row_dict.get("blocking_user"),
                            "host": row_dict.get("blocking_host"),
                            "database": row_dict.get("blocking_db"),
                            "command": row_dict.get("blocking_command"),
                            "state": row_dict.get("blocking_state"),
                            "query": row_dict.get("blocking_query"),
                            "duration_seconds": blocking_duration,
                        },
                        "lock_info": {
                            "blocked_lock_type": row_dict.get("blocked_lock_type"),
                            "blocked_lock_mode": row_dict.get("blocked_lock_mode"),
                            "blocked_lock_status": row_dict.get("blocked_lock_status"),
                            "blocked_lock_data": row_dict.get("blocked_lock_data"),
                            "blocking_lock_type": row_dict.get("blocking_lock_type"),
                            "blocking_lock_mode": row_dict.get("blocking_lock_mode"),
                            "blocking_lock_status": row_dict.get(
                                "blocking_lock_status"
                            ),
                            "blocking_lock_data": row_dict.get("blocking_lock_data"),
                            "affected_objects": ", ".join(affected_objects),
                            "requesting_lock_id": row_dict.get("requesting_lock_id"),
                            "blocking_lock_id": row_dict.get("blocking_lock_id"),
                        },
                    }
                )

            return blocking_data

        except Exception as e:
            logger.error(f"Error getting blocking data: {e}")
            return []

    async def _generate_lock_wait_graph(
        self, blocking_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate visual representation of blocking hierarchies."""
        try:
            graph = {
                "nodes": [],
                "edges": [],
                "visualization_data": {
                    "blocking_chains": [],
                    "root_blockers": [],
                    "leaf_blocked": [],
                },
            }

            # Build nodes and edges
            all_thread_ids = set()
            blocking_relationships = {}

            for block in blocking_data:
                blocked_thread_id = block["blocked_process"]["thread_id"]
                blocking_thread_id = block["blocking_process"]["thread_id"]

                all_thread_ids.add(blocked_thread_id)
                if blocking_thread_id:
                    all_thread_ids.add(blocking_thread_id)
                    blocking_relationships[blocked_thread_id] = blocking_thread_id

            # Create nodes
            nodes_list = []  # type: ignore
            for thread_id in all_thread_ids:
                # Find process info
                process_info = None
                for block in blocking_data:
                    if block["blocked_process"]["thread_id"] == thread_id:
                        process_info = block["blocked_process"]
                        break
                    elif block["blocking_process"]["thread_id"] == thread_id:
                        process_info = block["blocking_process"]
                        break

                if process_info:
                    nodes_list.append(
                        {
                            "thread_id": thread_id,
                            "user": process_info.get("user", "unknown"),
                            "host": process_info.get("host", "unknown"),
                            "database": process_info.get("database", "unknown"),
                            "state": process_info.get("state", "unknown"),
                            "duration": process_info.get("duration_seconds", 0),
                            "is_blocker": thread_id
                            in [
                                b["blocking_process"]["thread_id"]
                                for b in blocking_data
                                if b["blocking_process"]["thread_id"]
                            ],
                            "is_blocked": thread_id
                            in [
                                b["blocked_process"]["thread_id"] for b in blocking_data
                            ],
                        }
                    )

            graph["nodes"] = nodes_list  # type: ignore

            # Create edges
            edges_list = []  # type: ignore
            for blocked_thread_id, blocking_thread_id in blocking_relationships.items():
                edges_list.append(
                    {
                        "from": blocking_thread_id,
                        "to": blocked_thread_id,
                        "relationship": "blocks",
                    }
                )

            graph["edges"] = edges_list  # type: ignore

            # Analyze blocking chains
            chains = self._find_blocking_chains(blocking_relationships)
            graph["visualization_data"]["blocking_chains"] = chains  # type: ignore

            # Find root blockers (processes that block others but aren't blocked)
            root_blockers = []
            for thread_id in all_thread_ids:
                is_blocker = any(
                    rel[1] == thread_id for rel in blocking_relationships.items()
                )
                is_blocked = thread_id in blocking_relationships
                if is_blocker and not is_blocked:
                    root_blockers.append(thread_id)
            graph["visualization_data"]["root_blockers"] = root_blockers  # type: ignore

            # Find leaf blocked (processes that are blocked but don't block others)
            leaf_blocked = []
            for thread_id in all_thread_ids:
                is_blocked = thread_id in blocking_relationships
                is_blocker = any(
                    rel[1] == thread_id for rel in blocking_relationships.items()
                )
                if is_blocked and not is_blocker:
                    leaf_blocked.append(thread_id)
            graph["visualization_data"]["leaf_blocked"] = leaf_blocked  # type: ignore

            return graph

        except Exception as e:
            logger.error(f"Error generating lock wait graph: {e}")
            return {"error": str(e)}

    def _find_blocking_chains(
        self, blocking_relationships: Dict[int, int]
    ) -> List[List[int]]:
        """Find chains of blocking relationships."""
        chains = []
        visited = set()

        for blocked_thread_id in blocking_relationships:
            if blocked_thread_id in visited:
                continue

            chain = []
            current = blocked_thread_id

            # Follow the chain backwards to find the root
            while current in blocking_relationships:
                if current in chain:  # Circular dependency detected
                    break
                chain.append(current)
                current = blocking_relationships[current]
                visited.add(current)

            if current not in chain:
                chain.append(current)  # Add the root blocker

            if len(chain) > 1:
                chains.append(
                    list(reversed(chain))
                )  # Reverse to show blocker -> blocked

        return chains

    async def _get_deadlock_analysis(self) -> Dict[str, Any]:
        """Enhanced deadlock detection and analysis using MySQL variables and status."""
        try:
            # Get deadlock-related settings
            settings_query = """
                SELECT 
                    VARIABLE_NAME,
                    VARIABLE_VALUE
                FROM performance_schema.global_variables 
                WHERE VARIABLE_NAME IN (
                    'innodb_lock_wait_timeout',
                    'innodb_deadlock_detect',
                    'innodb_print_all_deadlocks',
                    'lock_wait_timeout'
                );
            """

            settings_result = await self.db_manager.execute_query(settings_query)
            settings = {}
            if settings_result.has_results:
                for row in settings_result.rows:
                    row_dict = dict(zip(settings_result.columns, row))
                    settings[row_dict["VARIABLE_NAME"]] = {
                        "value": row_dict["VARIABLE_VALUE"],
                        "description": self._get_setting_description(
                            row_dict["VARIABLE_NAME"]
                        ),
                    }

            # Get deadlock statistics
            deadlock_stats_query = """
                SELECT 
                    VARIABLE_NAME,
                    VARIABLE_VALUE
                FROM performance_schema.global_status
                WHERE VARIABLE_NAME LIKE '%deadlock%'
                   OR VARIABLE_NAME LIKE '%lock_wait%'
                   OR VARIABLE_NAME = 'Innodb_row_lock_waits';
            """

            stats_result = await self.db_manager.execute_query(deadlock_stats_query)
            deadlock_stats = {}
            if stats_result.has_results:
                for row in stats_result.rows:
                    row_dict = dict(zip(stats_result.columns, row))
                    deadlock_stats[row_dict["VARIABLE_NAME"]] = row_dict[
                        "VARIABLE_VALUE"
                    ]

            return {
                "settings": settings,
                "statistics": deadlock_stats,
                "analysis_timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error analyzing deadlocks: {e}")
            return {"error": str(e)}

    def _get_setting_description(self, setting_name: str) -> str:
        """Get description for MySQL settings."""
        descriptions = {
            "innodb_lock_wait_timeout": "Number of seconds an InnoDB transaction waits for a row lock",
            "innodb_deadlock_detect": "Enable/disable InnoDB deadlock detection",
            "innodb_print_all_deadlocks": "Print information about all deadlocks to MySQL error log",
            "lock_wait_timeout": "Timeout in seconds for attempts to acquire metadata locks",
        }
        return descriptions.get(setting_name, "MySQL system variable")

    async def _generate_session_termination_recommendations(
        self, blocking_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate recommendations for which sessions to terminate to resolve blocking."""
        recommendations = []

        try:
            # Analyze blocking impact
            blocker_impact: Dict[int, Dict[str, Any]] = {}  # type: ignore

            for block in blocking_data:
                blocking_thread_id = block["blocking_process"]["thread_id"]
                if not blocking_thread_id:
                    continue

                if blocking_thread_id not in blocker_impact:
                    blocker_impact[blocking_thread_id] = {
                        "blocked_sessions": [],
                        "total_wait_time": 0,
                        "blocking_duration": block["blocking_process"][
                            "duration_seconds"
                        ],
                        "process_info": block["blocking_process"],
                    }

                blocker_impact[blocking_thread_id]["blocked_sessions"].append(
                    block["blocked_process"]["thread_id"]
                )
                blocker_impact[blocking_thread_id]["total_wait_time"] += block[
                    "blocked_process"
                ]["duration_seconds"]

            # Generate termination recommendations
            for blocking_thread_id, impact in blocker_impact.items():
                priority = "HIGH"
                if impact["total_wait_time"] > 300:  # 5 minutes total wait
                    priority = "CRITICAL"
                elif impact["total_wait_time"] < 60:  # 1 minute total wait
                    priority = "LOW"

                recommendation = {
                    "target_thread_id": blocking_thread_id,
                    "priority": priority,
                    "reason": f"Blocking {len(impact['blocked_sessions'])} sessions for {impact['total_wait_time']:.1f} total seconds",
                    "blocked_sessions_count": len(impact["blocked_sessions"]),
                    "total_wait_time": impact["total_wait_time"],
                    "blocking_duration": impact["blocking_duration"],
                    "termination_command": f"KILL {blocking_thread_id};",
                    "process_info": {
                        "user": impact["process_info"]["user"],
                        "host": impact["process_info"]["host"],
                        "database": impact["process_info"]["database"],
                        "state": impact["process_info"]["state"],
                    },
                    "impact_assessment": self._assess_termination_impact(impact),
                }

                recommendations.append(recommendation)

            # Sort by priority
            priority_order = {"CRITICAL": 0, "HIGH": 1, "LOW": 2}
            recommendations.sort(key=lambda x: priority_order.get(x["priority"], 3))

            return recommendations

        except Exception as e:
            logger.error(f"Error generating session termination recommendations: {e}")
            return []

    def _assess_termination_impact(self, impact: Dict[str, Any]) -> str:
        """Assess the impact of terminating a blocking session."""
        if impact["blocking_duration"] > 1800:  # 30 minutes
            return "LOW_RISK - Long-running session likely stuck"
        elif impact["total_wait_time"] > impact["blocking_duration"] * 2:
            return "MEDIUM_RISK - Blocking multiple sessions significantly"
        else:
            return "HIGH_RISK - Consider alternative solutions first"

    async def _generate_lock_timeout_suggestions(
        self, blocking_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate optimal lock timeout suggestions based on current blocking patterns."""
        try:
            # Get current timeout settings
            current_settings_query = """
                SELECT 
                    VARIABLE_NAME,
                    VARIABLE_VALUE
                FROM performance_schema.global_variables
                WHERE VARIABLE_NAME IN (
                    'innodb_lock_wait_timeout',
                    'lock_wait_timeout'
                );
            """

            result = await self.db_manager.execute_query(current_settings_query)
            current_settings = {}
            if result.has_results:
                for row in result.rows:
                    row_dict = dict(zip(result.columns, row))
                    current_settings[row_dict["VARIABLE_NAME"]] = row_dict[
                        "VARIABLE_VALUE"
                    ]

            # Analyze wait times to suggest optimal timeouts
            wait_times = [
                block["blocked_process"]["duration_seconds"] for block in blocking_data
            ]

            if wait_times:
                avg_wait = sum(wait_times) / len(wait_times)
                max_wait = max(wait_times)

                # Suggest innodb_lock_wait_timeout based on analysis
                suggested_innodb_timeout = min(
                    max(avg_wait * 2, 30), 300
                )  # Between 30s and 5min

                # Suggest lock_wait_timeout based on blocking patterns
                suggested_lock_timeout = min(
                    max(max_wait * 1.5, 60), 600
                )  # Between 1min and 10min

                suggestions = {
                    "current_settings": current_settings,
                    "analysis": {
                        "average_wait_time": avg_wait,
                        "maximum_wait_time": max_wait,
                        "total_blocking_sessions": len(blocking_data),
                    },
                    "recommendations": {
                        "innodb_lock_wait_timeout": {
                            "suggested_value": f"{int(suggested_innodb_timeout)}",
                            "reason": f"Based on average wait time of {avg_wait:.1f}s, suggest {int(suggested_innodb_timeout)}s to prevent excessive blocking",
                        },
                        "lock_wait_timeout": {
                            "suggested_value": f"{int(suggested_lock_timeout)}",
                            "reason": f"Based on maximum wait time of {max_wait:.1f}s, suggest {int(suggested_lock_timeout)}s to prevent metadata lock waits",
                        },
                    },
                }
            else:
                suggestions = {
                    "current_settings": current_settings,
                    "recommendations": {
                        "innodb_lock_wait_timeout": {
                            "suggested_value": "50",
                            "reason": "Standard recommendation for OLTP workloads",
                        },
                        "lock_wait_timeout": {
                            "suggested_value": "120",
                            "reason": "Standard recommendation for metadata lock timeout",
                        },
                    },
                }

            return suggestions

        except Exception as e:
            logger.error(f"Error generating lock timeout suggestions: {e}")
            return {"error": str(e)}

    async def _get_historical_blocking_analysis(self) -> Dict[str, Any]:
        """Analyze long-running sessions that could be potential blocking sources."""
        try:
            long_running_query = """
                SELECT 
                    ID as thread_id,
                    USER as user,
                    HOST as host,
                    DB as database,
                    COMMAND as command,
                    TIME as duration_seconds,
                    STATE as state,
                    INFO as query
                FROM information_schema.processlist
                WHERE COMMAND != 'Sleep'
                    AND TIME > 300  -- 5 minutes
                ORDER BY TIME DESC
                LIMIT 20;
            """

            result = await self.db_manager.execute_query(long_running_query)
            long_running_sessions = []

            if result.has_results:
                for row in result.rows:
                    row_dict = dict(zip(result.columns, row))
                    long_running_sessions.append(
                        {
                            "thread_id": row_dict.get("thread_id"),
                            "user": row_dict.get("user"),
                            "host": row_dict.get("host"),
                            "database": row_dict.get("database"),
                            "command": row_dict.get("command"),
                            "duration_seconds": float(
                                row_dict.get("duration_seconds", 0)
                            ),
                            "state": row_dict.get("state"),
                            "query": row_dict.get("query"),
                        }
                    )

            return {
                "long_running_sessions": long_running_sessions,
                "analysis": {
                    "total_long_running": len(long_running_sessions),
                    "potential_blocking_sources": [
                        s
                        for s in long_running_sessions
                        if s["duration_seconds"] > 1800  # 30 minutes
                    ],
                    "recommendations": [
                        "Monitor these long-running sessions as potential blocking sources",
                        "Consider implementing connection pooling to limit session duration",
                        "Review application logic for long-running transactions",
                        "Set appropriate innodb_lock_wait_timeout values",
                    ],
                },
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error analyzing historical blocking patterns: {e}")
            return {"error": str(e)}

    async def _get_lock_contention_hotspots(self) -> Dict[str, Any]:
        """Identify specific tables with frequent lock contention using performance schema."""
        try:
            hotspot_query = """
                SELECT 
                    OBJECT_SCHEMA,
                    OBJECT_NAME,
                    COUNT(*) as lock_count,
                    COUNT(DISTINCT ENGINE_TRANSACTION_ID) as transaction_count,
                    GROUP_CONCAT(DISTINCT LOCK_TYPE) as lock_types,
                    GROUP_CONCAT(DISTINCT LOCK_MODE) as lock_modes
                FROM performance_schema.data_locks 
                WHERE OBJECT_SCHEMA IS NOT NULL 
                    AND OBJECT_NAME IS NOT NULL
                    AND OBJECT_SCHEMA NOT IN ('mysql', 'information_schema', 'performance_schema', 'sys')
                GROUP BY OBJECT_SCHEMA, OBJECT_NAME
                HAVING lock_count > 1
                ORDER BY lock_count DESC, transaction_count DESC
                LIMIT 20;
            """

            result = await self.db_manager.execute_query(hotspot_query)
            hotspots = []

            if result.has_results:
                for row in result.rows:
                    row_dict = dict(zip(result.columns, row))
                    lock_count = int(row_dict.get("lock_count", 0))
                    hotspots.append(
                        {
                            "schema": row_dict.get("OBJECT_SCHEMA"),
                            "table": row_dict.get("OBJECT_NAME"),
                            "lock_count": lock_count,
                            "transaction_count": row_dict.get("transaction_count"),
                            "lock_types": row_dict.get("lock_types"),
                            "lock_modes": row_dict.get("lock_modes"),
                            "contention_risk": "HIGH" if lock_count > 10 else "MEDIUM",
                        }
                    )

            return {
                "contention_hotspots": hotspots,
                "analysis": {
                    "high_risk_tables": len(
                        [h for h in hotspots if h["contention_risk"] == "HIGH"]
                    ),
                    "total_analyzed": len(hotspots),
                },
                "recommendations": [
                    "Monitor high-activity tables for lock contention",
                    "Consider query optimization for frequently locked tables",
                    "Review indexing strategy for frequently modified tables",
                    "Consider table partitioning for very large, active tables",
                ]
                if hotspots
                else [],
            }

        except Exception as e:
            logger.error(f"Error identifying lock contention hotspots: {e}")
            return {"error": str(e)}

    def _check_lock_wait_thresholds(
        self, blocking_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Check for configurable alerts for long-running lock waits."""
        alerts = []

        # Configurable thresholds
        thresholds = {
            "WARNING": 60,  # 1 minute
            "CRITICAL": 300,  # 5 minutes
            "EMERGENCY": 900,  # 15 minutes
        }

        for block in blocking_data:
            wait_time = block["blocked_process"]["duration_seconds"]

            for level, threshold in thresholds.items():
                if wait_time >= threshold:
                    alerts.append(
                        {
                            "level": level,
                            "threshold": threshold,
                            "actual_wait_time": wait_time,
                            "blocked_thread_id": block["blocked_process"]["thread_id"],
                            "blocking_thread_id": block["blocking_process"][
                                "thread_id"
                            ],
                            "message": f"{level}: Thread {block['blocked_process']['thread_id']} has been waiting for {wait_time:.1f}s (threshold: {threshold}s)",
                        }
                    )
                    break  # Only add the highest applicable alert level

        return alerts

    async def _generate_healthy_recommendations(self) -> List[str]:
        """Generate compact recommendations when no blocking is detected."""
        return [
            "monitor_lock_patterns",
            "review_query_performance",
            "check_indexing",
            "monitor_timeout_settings",
            "check_deadlock_stats",
        ]

    async def _generate_enhanced_recommendations(
        self,
        blocking_data: List[Dict[str, Any]],
        summary: Dict[str, Any],
        session_termination_recs: List[Dict[str, Any]],
        lock_timeout_suggestions: Dict[str, Any],
        historical_analysis: Dict[str, Any],
    ) -> List[str]:
        """Generate compact enhanced recommendations for agents."""
        recommendations = []

        # Start with basic recommendations
        basic_recs = self._generate_recommendations(blocking_data, summary)
        recommendations.extend(basic_recs)

        # Add session termination recommendations (compact)
        if session_termination_recs:
            for rec in session_termination_recs[:3]:  # Top 3 recommendations
                recommendations.append(
                    f"KILL_THREAD_{rec['target_thread_id']}_{rec['priority']}: {rec['reason'][:50]}..."
                )

        # Add timeout suggestions (compact)
        if lock_timeout_suggestions.get("recommendations"):
            for setting, config in lock_timeout_suggestions["recommendations"].items():
                recommendations.append(
                    f"TIMEOUT_{setting.upper()}: {config['suggested_value']}s"
                )

        # Add historical analysis insights (compact)
        if historical_analysis.get("analysis", {}).get("potential_blocking_sources"):
            count = len(historical_analysis["analysis"]["potential_blocking_sources"])
            recommendations.append(f"HISTORICAL_LONG_RUNNING: {count}_sessions")

        return recommendations

    def _generate_recommendations(
        self, blocking_data: List[Dict[str, Any]], summary: Dict[str, Any]
    ) -> List[str]:
        """Generate compact recommendations for agent consumption."""
        recommendations = []

        if summary["max_wait_time_seconds"] > 300:  # 5 minutes
            recommendations.append(
                f"CRITICAL_BLOCKING: {summary['max_wait_time_seconds']:.1f}s_max_wait_terminate_sessions"
            )
        elif summary["max_wait_time_seconds"] > 60:  # 1 minute
            recommendations.append(
                f"WARNING_BLOCKING: {summary['max_wait_time_seconds']:.1f}s_max_wait_monitor"
            )

        if summary["total_blocked"] > 10:
            recommendations.append(
                f"HIGH_CONTENTION: {summary['total_blocked']}_blocked_queries_review_patterns"
            )

        # Analyze lock types (compact)
        lock_types = {}
        for block in blocking_data:
            blocked_lock_type = block["lock_info"]["blocked_lock_type"]
            if blocked_lock_type:
                lock_types[blocked_lock_type] = lock_types.get(blocked_lock_type, 0) + 1

        if "RECORD" in lock_types and lock_types["RECORD"] > 3:
            recommendations.append(
                f"ROW_LOCKS_HIGH: {lock_types['RECORD']}_record_locks_optimize_queries"
            )

        if "TABLE" in lock_types:
            recommendations.append("TABLE_LOCKS_DETECTED: review_scans_add_indexes")

        # Check for hotspots (compact)
        if len(summary["affected_relations"]) < summary["total_blocked"] / 2:
            relations = ",".join(summary["affected_relations"])
            recommendations.append(f"LOCK_HOTSPOT: focus_tables_{relations}")

        if not recommendations:
            recommendations.append("BLOCKING_MANAGEABLE: monitor_patterns")

        return recommendations

    def _format_as_text(self, result: Dict[str, Any]) -> str:
        """Format blocking queries analysis result as token-efficient text for agents."""
        # Return structured JSON-like output for agent consumption
        output_lines = []

        status = result.get("status", "unknown")
        summary = result.get("summary", {})
        blocking_queries = result.get("blocking_queries", [])

        # Compact status summary
        output_lines.append(f"STATUS: {status}")

        if status == "healthy":
            output_lines.append(
                f"MESSAGE: {result.get('message', 'No blocking detected')}"
            )
            output_lines.append(
                f"EXEC_TIME: {result.get('execution_metadata', {}).get('execution_time_seconds', 0):.2f}s"
            )
            return "\n".join(output_lines)

        # Summary metrics
        output_lines.append("SUMMARY:")
        output_lines.append(f"  blocked: {summary.get('total_blocked', 0)}")
        output_lines.append(f"  blocking: {summary.get('total_blocking', 0)}")
        output_lines.append(
            f"  max_wait: {summary.get('max_wait_time_seconds', 0):.1f}s"
        )
        if summary.get("affected_relations"):
            output_lines.append(
                f"  relations: {','.join(summary.get('affected_relations', []))}"
            )

        # Blocking queries in compact format
        if blocking_queries:
            output_lines.append("BLOCKING:")
            for block in blocking_queries:
                blocked = block.get("blocked_process", {})
                blocking = block.get("blocking_process", {})
                lock = block.get("lock_info", {})

                # Single line per blocking relationship
                blocked_info = f"tid:{blocked.get('thread_id')} user:{blocked.get('user')} db:{blocked.get('database')} wait:{blocked.get('duration_seconds', 0):.1f}s"
                blocking_info = f"tid:{blocking.get('thread_id')} user:{blocking.get('user')} db:{blocking.get('database')} dur:{blocking.get('duration_seconds', 0):.1f}s"
                lock_info = f"type:{lock.get('blocked_lock_type')} mode:{lock.get('blocked_lock_mode')}"

                output_lines.append(
                    f"  {blocked_info} <- {blocking_info} [{lock_info}]"
                )

                # Add query info if available (truncated to 50 chars for efficiency)
                if blocked.get("query"):
                    query = (
                        blocked["query"][:50] + "..."
                        if len(blocked["query"]) > 50
                        else blocked["query"]
                    )
                    output_lines.append(f"    blocked_query: {query}")
                if blocking.get("query"):
                    query = (
                        blocking["query"][:50] + "..."
                        if len(blocking["query"]) > 50
                        else blocking["query"]
                    )
                    output_lines.append(f"    blocking_query: {query}")

        # Priority recommendations only
        recommendations = result.get("recommendations", [])
        if recommendations:
            output_lines.append("PRIORITY_ACTIONS:")
            for rec in recommendations[:5]:  # Limit to top 5 for efficiency
                # Extract priority indicators
                if "CRITICAL" in rec or "HIGH" in rec:
                    output_lines.append(f"  {rec.replace(chr(10), ' ')}")

        # Execution metadata
        exec_meta = result.get("execution_metadata", {})
        output_lines.append(
            f"EXEC_TIME: {exec_meta.get('execution_time_seconds', 0):.2f}s"
        )
        output_lines.append(f"TIMESTAMP: {exec_meta.get('timestamp', 'N/A')}")

        return "\n".join(output_lines)

    def _format_timeout_result(self, timeout: int) -> str:
        """Format timeout error result for agents."""
        return f"""STATUS: timeout
TIMEOUT_SECONDS: {timeout}
CAUSE: high_load|complex_analysis|resource_constraints
RECOMMENDATIONS: retry_offpeak|increase_timeout|check_resources|review_connections"""

    def _format_error_result(self, error: str) -> str:
        """Format general error result for agents."""
        error_clean = error.replace("\n", " | ")
        return f"""STATUS: error
ERROR: {error_clean}
TROUBLESHOOTING: check_connection|verify_performance_schema|check_privileges|review_error_log"""


# Create the tool function that will be exposed to the MCP server
async def get_blocking_queries_tool(db_manager, timeout: int = 300) -> str:
    """
    Analyze MySQL blocking queries and lock contention.

    Args:
        db_manager: Database manager instance
        timeout: Maximum execution time in seconds (default: 300)

    Returns:
        Comprehensive blocking queries analysis report
    """
    analyzer = BlockingQueriesAnalyzer(db_manager)
    return await analyzer.get_blocking_queries(timeout=timeout)
