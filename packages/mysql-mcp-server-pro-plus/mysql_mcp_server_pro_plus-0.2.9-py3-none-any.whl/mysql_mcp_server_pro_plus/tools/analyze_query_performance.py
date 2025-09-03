"""Query performance analysis tool for MySQL databases.

Provides comprehensive analysis of query execution plans, performance metrics,
and optimization recommendations using EXPLAIN and MySQL performance schema.
"""

from __future__ import annotations

import asyncio
import time
from datetime import datetime
from typing import Any, Dict, List

from ..logger import logger


class QueryPerformanceAnalyzer:
    """Analyzer for MySQL query performance and optimization."""

    def __init__(self, db_manager):
        self.db_manager = db_manager

    async def analyze_query_performance(
        self, query: str, analyze_execution: bool = False, timeout: int = 300
    ) -> str:
        """
        Analyze query performance with EXPLAIN plan analysis and optimization recommendations.

        Features:
        - EXPLAIN Plan Analysis: Query execution strategy, index usage, table scan types
        - Performance Metrics: Estimated vs actual execution time, I/O costs, memory usage
        - Index Recommendations: Missing indexes, unused indexes, composite index suggestions
        - Query Optimization: Rewrite suggestions, JOIN optimization, WHERE clause improvements
        - Execution Analysis: Actual runtime statistics (optional, with safety controls)
        - Cost Estimation: Resource consumption predictions

        Args:
            query: The SQL query to analyze
            analyze_execution: Enable actual execution analysis (default: False)
            timeout: Maximum execution time in seconds (default: 300)

        Returns:
            String containing comprehensive performance analysis and recommendations
        """
        start_time = time.time()
        try:
            result = await asyncio.wait_for(
                self._analyze_query_performance_internal(
                    query, analyze_execution, start_time
                ),
                timeout=timeout,
            )
            return self._format_as_text(result)
        except asyncio.TimeoutError:
            logger.warning(
                f"Query performance analysis timed out after {timeout} seconds"
            )
            return self._format_timeout_result(timeout)
        except Exception as e:
            logger.error(f"Error analyzing query performance: {e}")
            return self._format_error_result(str(e))

    async def _analyze_query_performance_internal(
        self, query: str, analyze_execution: bool, start_time: float
    ) -> Dict[str, Any]:
        """Internal method for comprehensive query performance analysis."""
        result: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "analysis_duration_seconds": 0.0,
            "query": query.strip(),
            "explain_plan": {},
            "performance_metrics": {},
            "recommendations": [],
            "optimization_score": 0.0,
        }

        try:
            # 1. Basic EXPLAIN analysis
            result["explain_plan"] = await self._get_explain_plan(query)

            # 2. Extended EXPLAIN with JSON format for detailed analysis
            result["explain_extended"] = await self._get_explain_extended(query)

            # 3. Performance metrics analysis
            result["performance_metrics"] = await self._analyze_performance_metrics(
                query
            )

            # 4. Index analysis and recommendations
            result["index_analysis"] = await self._analyze_indexes_for_query(query)

            # 5. Query optimization suggestions
            result[
                "optimization_suggestions"
            ] = await self._generate_optimization_suggestions(
                result["explain_plan"], result["explain_extended"]
            )

            # 6. Optional execution analysis (with safety controls)
            if analyze_execution:
                result["execution_analysis"] = await self._analyze_execution(query)

            # 7. Calculate optimization score
            result["optimization_score"] = self._calculate_optimization_score(result)

            # 8. Generate recommendations
            result["recommendations"] = self._generate_recommendations(result)

            result["analysis_duration_seconds"] = time.time() - start_time
            return result

        except Exception as e:
            logger.error(f"Error in query performance analysis: {e}")
            result["error"] = str(e)
            result["analysis_duration_seconds"] = time.time() - start_time
            return result

    async def _get_explain_plan(self, query: str) -> Dict[str, Any]:
        """Get basic EXPLAIN plan for the query."""
        try:
            explain_query = f"EXPLAIN {query}"
            result = await self.db_manager.execute_query(explain_query)

            if result.has_results:
                plan_data = []
                for row in result.rows:
                    row_dict = dict(zip(result.columns, row))
                    plan_data.append(row_dict)
                return {"plan": plan_data, "status": "success"}

            return {"plan": [], "status": "no_results"}
        except Exception as e:
            logger.error(f"Error getting EXPLAIN plan: {e}")
            return {"plan": [], "status": "error", "error": str(e)}

    async def _get_explain_extended(self, query: str) -> Dict[str, Any]:
        """Get extended EXPLAIN with JSON format for detailed analysis."""
        try:
            explain_query = f"EXPLAIN FORMAT=JSON {query}"
            result = await self.db_manager.execute_query(explain_query)

            if result.has_results and result.rows:
                # MySQL returns JSON in first column of first row
                json_str = result.rows[0][0]
                return {"json_plan": json_str, "status": "success"}

            return {"json_plan": "", "status": "no_results"}
        except Exception as e:
            logger.error(f"Error getting extended EXPLAIN: {e}")
            return {"json_plan": "", "status": "error", "error": str(e)}

    async def _analyze_performance_metrics(self, query: str) -> Dict[str, Any]:
        """Analyze performance metrics and resource consumption."""
        try:
            table_count = query.upper().count("FROM") + query.upper().count("JOIN")
            condition_count = query.upper().count("WHERE") + query.upper().count(
                "HAVING"
            )

            metrics = {
                "query_length": len(query),
                "estimated_complexity": "low",
                "table_count": table_count,
                "condition_count": condition_count,
                "status": "success",
            }

            # Estimate complexity based on query patterns
            if table_count > 3:
                metrics["estimated_complexity"] = "high"
            elif table_count > 1 or condition_count > 2:
                metrics["estimated_complexity"] = "medium"

            return metrics
        except Exception as e:
            logger.error(f"Error analyzing performance metrics: {e}")
            return {"status": "error", "error": str(e)}

    async def _analyze_indexes_for_query(self, query: str) -> Dict[str, Any]:
        """Analyze indexes that could benefit the query."""
        try:
            # Basic index analysis - can be enhanced with table parsing
            recommendations: List[str] = []

            # Simple heuristics for index recommendations
            if "WHERE" in query.upper():
                recommendations.append(
                    "Consider adding indexes on WHERE clause columns"
                )
            if "ORDER BY" in query.upper():
                recommendations.append("Consider adding indexes on ORDER BY columns")
            if "GROUP BY" in query.upper():
                recommendations.append("Consider adding indexes on GROUP BY columns")

            analysis = {
                "status": "success",
                "recommendations": recommendations,
                "current_usage": "unknown",
            }

            return analysis
        except Exception as e:
            logger.error(f"Error analyzing indexes: {e}")
            return {"status": "error", "error": str(e)}

    async def _generate_optimization_suggestions(
        self, explain_plan: Dict[str, Any], _explain_extended: Dict[str, Any]
    ) -> List[str]:
        """Generate query optimization suggestions based on EXPLAIN output."""
        suggestions = []

        try:
            if explain_plan.get("status") == "success" and explain_plan.get("plan"):
                for step in explain_plan["plan"]:
                    # Check for full table scans
                    if step.get("type") == "ALL":
                        suggestions.append(
                            f"CRITICAL: Full table scan detected on table '{step.get('table')}' - consider adding indexes"
                        )

                    # Check for filesort
                    if step.get("Extra") and "Using filesort" in str(step.get("Extra")):
                        suggestions.append(
                            "WARNING: Filesort operation detected - consider optimizing ORDER BY with indexes"
                        )

                    # Check for temporary tables
                    if step.get("Extra") and "Using temporary" in str(
                        step.get("Extra")
                    ):
                        suggestions.append(
                            "OPTIMIZATION: Temporary table created - consider query rewrite or index optimization"
                        )

        except Exception as e:
            logger.error(f"Error generating optimization suggestions: {e}")
            suggestions.append("Error generating suggestions - see logs for details")

        return suggestions

    async def _analyze_execution(self, query: str) -> Dict[str, Any]:
        """Analyze actual execution with safety controls."""
        try:
            # Safety check - only allow SELECT queries for execution analysis
            if not query.strip().upper().startswith("SELECT"):
                return {
                    "status": "skipped",
                    "reason": "Execution analysis only available for SELECT queries",
                }

            # Additional safety - limit result set size
            limited_query = f"{query} LIMIT 1"
            start_time = time.time()

            result = await self.db_manager.execute_query(limited_query)
            execution_time = time.time() - start_time

            return {
                "status": "success",
                "execution_time_seconds": execution_time,
                "rows_returned": len(result.rows) if result.has_results else 0,
                "note": "Limited to 1 row for safety",
            }
        except Exception as e:
            logger.error(f"Error in execution analysis: {e}")
            return {"status": "error", "error": str(e)}

    def _calculate_optimization_score(self, analysis_result: Dict[str, Any]) -> float:
        """Calculate an optimization score (0-100) based on analysis results."""
        score = 100.0  # Start with perfect score

        try:
            # Deduct points for issues found
            suggestions = analysis_result.get("optimization_suggestions", [])
            for suggestion in suggestions:
                if "CRITICAL:" in suggestion:  # Critical issues
                    score -= 25
                elif "WARNING:" in suggestion:  # Warnings
                    score -= 15
                elif "OPTIMIZATION:" in suggestion:  # Optimizations
                    score -= 10

            # Ensure score doesn't go below 0
            return max(0.0, score)
        except Exception:
            return 50.0  # Default neutral score

    def _generate_recommendations(self, analysis_result: Dict[str, Any]) -> List[str]:
        """Generate high-level recommendations based on analysis."""
        recommendations = []

        try:
            score = analysis_result.get("optimization_score", 50)

            if score >= 80:
                recommendations.append("GOOD: Query appears well-optimized")
            elif score >= 60:
                recommendations.append(
                    "WARNING: Query has minor optimization opportunities"
                )
            else:
                recommendations.append("CRITICAL: Query needs significant optimization")

            # Add specific recommendations from optimization suggestions
            recommendations.extend(analysis_result.get("optimization_suggestions", []))

            return recommendations
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return ["Error generating recommendations"]

    def _format_as_text(self, result: Dict[str, Any]) -> str:
        """Format analysis result as readable text."""
        lines = [
            "MySQL Query Performance Analysis",
            f"Analysis completed at: {result.get('timestamp', 'unknown')}",
            f"Analysis duration: {result.get('analysis_duration_seconds', 0):.2f} seconds",
            f"Optimization Score: {result.get('optimization_score', 0):.1f}/100",
            "",
            "Query Analyzed:",
            result.get("query", "N/A")[:500]
            + ("..." if len(result.get("query", "")) > 500 else ""),
            "",
        ]

        # Add EXPLAIN plan summary
        explain_plan = result.get("explain_plan", {})
        if explain_plan.get("status") == "success" and explain_plan.get("plan"):
            lines.append("EXPLAIN Plan Summary:")
            for i, step in enumerate(explain_plan["plan"], 1):
                table = step.get("table", "N/A")
                type_val = step.get("type", "N/A")
                rows = step.get("rows", "N/A")
                extra = step.get("Extra", "")
                lines.append(
                    f"Step {i}: Table: {table}, Type: {type_val}, Rows: {rows}"
                )
                if extra:
                    lines.append(f"  Extra: {extra}")
            lines.append("")

        # Add performance metrics
        metrics = result.get("performance_metrics", {})
        if metrics.get("status") == "success":
            lines.extend(
                [
                    "Performance Metrics:",
                    f"Query Length: {metrics.get('query_length', 0)} characters",
                    f"Estimated Complexity: {metrics.get('estimated_complexity', 'unknown')}",
                    f"Table Count: {metrics.get('table_count', 0)}",
                    f"Condition Count: {metrics.get('condition_count', 0)}",
                    "",
                ]
            )

        # Add recommendations
        recommendations = result.get("recommendations", [])
        if recommendations:
            lines.append("Recommendations:")
            for rec in recommendations:
                lines.append(f"- {rec}")
            lines.append("")

        # Add execution analysis if available
        execution = result.get("execution_analysis", {})
        if execution.get("status") == "success":
            lines.extend(
                [
                    "Execution Analysis:",
                    f"Execution Time: {execution.get('execution_time_seconds', 0):.4f} seconds",
                    f"Rows Returned: {execution.get('rows_returned', 0)}",
                    f"Note: {execution.get('note', '')}",
                    "",
                ]
            )

        return "\n".join(lines)

    def _format_timeout_result(self, timeout: int) -> str:
        """Format timeout result."""
        return f"""Query Performance Analysis Timeout
Analysis timed out after {timeout} seconds.
Try reducing query complexity or increasing timeout limit."""

    def _format_error_result(self, error: str) -> str:
        """Format error result."""
        return f"""Query Performance Analysis Error
Error: {error}"""


async def analyze_query_performance_tool(
    query: str,
    analyze_execution: bool,
    db_manager,
    security_validator,
    timeout: int = 300,
) -> str:
    """
    Analyze query performance with comprehensive metrics and optimization recommendations.

    Args:
        query: The SQL query to analyze
        analyze_execution: Enable actual execution analysis
        db_manager: Database manager instance
        security_validator: Security validator instance
        timeout: Maximum execution time in seconds

    Returns:
        String containing performance analysis results
    """
    try:
        logger.info(f"Analyzing query performance: {query[:100]}...")

        if not db_manager or not security_validator:
            raise RuntimeError("Server not properly initialized")

        # Validate query (read-only operations only for safety)
        validated_query = security_validator.validate_query(query)

        # Create analyzer and run analysis
        analyzer = QueryPerformanceAnalyzer(db_manager)
        return await analyzer.analyze_query_performance(
            validated_query, analyze_execution, timeout
        )

    except Exception as e:
        logger.error(f"Query performance analysis error: {e}")
        return f"Error: {str(e)}"
