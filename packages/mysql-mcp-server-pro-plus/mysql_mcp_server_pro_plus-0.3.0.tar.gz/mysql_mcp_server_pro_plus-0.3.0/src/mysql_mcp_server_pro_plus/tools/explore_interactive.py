"""Interactive data exploration tool for comprehensive MySQL table analysis.

Provides drill-down exploration, smart sampling, pattern discovery, relationship navigation,
time-series analysis, and comparative analysis capabilities.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..logger import logger


class InteractiveExplorer:
    """Advanced interactive data exploration tool for MySQL tables."""

    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.max_sample_size = 10000  # Maximum sample size for analysis
        self.anomaly_threshold = 3.0  # Standard deviations for anomaly detection

    async def explore_interactive(
        self,
        table_name: str,
        exploration_type: str = "drilldown",
        sample_size: int = 1000,
        filters: Optional[Dict[str, Any]] = None,
        group_by: Optional[List[str]] = None,
        order_by: Optional[str] = None,
        time_column: Optional[str] = None,
    ) -> str:
        """
        Interactive data exploration with multiple analysis modes.

        Args:
            table_name: Target table to explore
            exploration_type: Type of exploration ("drilldown", "patterns", "relationships",
                            "timeseries", "comparative", "sampling")
            sample_size: Number of records to sample (max 10,000)
            filters: Optional filters to apply
            group_by: Columns to group by for aggregation
            order_by: Column to order results by
            time_column: Column containing temporal data for time-series analysis

        Returns:
            Comprehensive exploration results as formatted text
        """
        try:
            # Validate inputs
            if sample_size > self.max_sample_size:
                sample_size = self.max_sample_size
                logger.warning(f"Sample size limited to {self.max_sample_size}")

            # Get basic table information
            table_info = await self._get_table_structure(table_name)

            # Execute exploration based on type
            if exploration_type == "drilldown":
                result = await self._explore_drilldown(
                    table_name, sample_size, filters, group_by, order_by
                )
            elif exploration_type == "patterns":
                result = await self._explore_patterns(table_name, sample_size)
            elif exploration_type == "relationships":
                result = await self._explore_relationships(table_name)
            elif exploration_type == "timeseries":
                result = await self._explore_timeseries(
                    table_name, time_column, sample_size
                )
            elif exploration_type == "comparative":
                result = await self._explore_comparative(
                    table_name, group_by, sample_size
                )
            elif exploration_type == "sampling":
                result = await self._explore_sampling(table_name, sample_size)
            else:
                raise ValueError(f"Unknown exploration type: {exploration_type}")

            # Format results
            return self._format_exploration_results(
                result, exploration_type, table_info
            )

        except Exception as e:
            logger.error(f"Error in interactive exploration: {e}")
            return f"Error: {str(e)}"

    async def _get_table_structure(self, table_name: str) -> Dict[str, Any]:
        """Get comprehensive table structure information."""
        # Get column information
        describe_query = f"DESCRIBE `{table_name}`"
        describe_result = await self.db_manager.execute_query(describe_query)

        columns = {}
        if describe_result.has_results:
            for row in describe_result.rows:
                col_name = row[0]
                col_type = row[1]
                nullable = row[2] == "YES"
                key = row[3]
                columns[col_name] = {
                    "type": col_type,
                    "nullable": nullable,
                    "key": key,
                    "is_numeric": any(
                        keyword in col_type.upper()
                        for keyword in ["INT", "DECIMAL", "FLOAT", "DOUBLE"]
                    ),
                    "is_temporal": any(
                        keyword in col_type.upper()
                        for keyword in ["DATE", "TIME", "DATETIME", "TIMESTAMP"]
                    ),
                    "is_text": any(
                        keyword in col_type.upper()
                        for keyword in ["VARCHAR", "TEXT", "CHAR"]
                    ),
                }

        # Get row count estimate
        count_query = f"SELECT table_rows FROM information_schema.TABLES WHERE table_name = '{table_name}' AND table_schema = DATABASE()"
        count_result = await self.db_manager.execute_query(count_query)
        total_rows = count_result.rows[0][0] if count_result.has_results else 0

        return {"columns": columns, "total_rows": total_rows, "table_name": table_name}

    async def _explore_drilldown(
        self,
        table_name: str,
        sample_size: int,
        filters: Optional[Dict[str, Any]] = None,
        group_by: Optional[List[str]] = None,
        order_by: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Drill-down exploration with hierarchical data analysis."""
        result: Dict[str, Any] = {
            "summary": {},
            "sample_data": [],
            "aggregations": {},
            "distribution_analysis": {},
            "data_quality": {},
        }

        try:
            # Build base query with sampling
            base_query = f"SELECT * FROM `{table_name}`"
            where_clause = self._build_where_clause(filters)
            if where_clause:
                base_query += f" WHERE {where_clause}"

            # Add ordering
            if order_by:
                base_query += f" ORDER BY `{order_by}`"

            # Add sampling limit
            base_query += f" LIMIT {sample_size}"

            # Execute sample query
            sample_result = await self.db_manager.execute_query(base_query)
            if sample_result.has_results:
                result["sample_data"] = sample_result.rows
                result["columns"] = sample_result.columns

            # Generate aggregations if group_by specified
            if group_by:
                agg_query = self._build_aggregation_query(table_name, group_by, filters)
                agg_result = await self.db_manager.execute_query(agg_query)
                if agg_result.has_results:
                    result["aggregations"] = {
                        "data": agg_result.rows,
                        "columns": agg_result.columns,
                    }

            # Analyze data distributions
            result["distribution_analysis"] = await self._analyze_distributions(
                table_name, sample_size, filters
            )

            # Data quality assessment
            result["data_quality"] = await self._assess_data_quality(
                table_name, sample_size
            )

        except Exception as e:
            logger.error(f"Error in drilldown exploration: {e}")
            result["error"] = str(e)

        return result

    async def _explore_patterns(
        self, table_name: str, sample_size: int
    ) -> Dict[str, Any]:
        """Discover patterns and anomalies in the data."""
        result: Dict[str, Any] = {
            "patterns": {},
            "anomalies": {},
            "correlations": {},
            "clusters": {},
        }

        try:
            # Get sample data for analysis
            sample_query = f"SELECT * FROM `{table_name}` LIMIT {sample_size}"
            sample_result = await self.db_manager.execute_query(sample_query)

            if sample_result.has_results:
                data = sample_result.rows
                columns = sample_result.columns

                # Analyze patterns in each column
                for i, col_name in enumerate(columns):
                    col_data = [row[i] for row in data if row[i] is not None]
                    if col_data:
                        result["patterns"][col_name] = self._analyze_column_patterns(
                            col_data, col_name
                        )

                # Detect anomalies
                result["anomalies"] = self._detect_anomalies(data, columns)

                # Find correlations between numeric columns
                result["correlations"] = self._analyze_correlations(data, columns)

        except Exception as e:
            logger.error(f"Error in pattern exploration: {e}")
            result["error"] = str(e)

        return result

    async def _explore_relationships(self, table_name: str) -> Dict[str, Any]:
        """Explore foreign key relationships and data dependencies."""
        result: Dict[str, Any] = {
            "foreign_keys": {},
            "referenced_by": {},
            "relationship_graph": {},
            "data_dependencies": {},
        }

        try:
            # Get foreign keys
            fk_query = f"""
                SELECT
                    constraint_name,
                    column_name,
                    referenced_table_name,
                    referenced_column_name
                FROM information_schema.KEY_COLUMN_USAGE
                WHERE table_name = '{table_name}'
                AND table_schema = DATABASE()
                AND referenced_table_name IS NOT NULL
                ORDER BY constraint_name, ordinal_position
            """
            fk_result = await self.db_manager.execute_query(fk_query)

            if fk_result.has_results:
                relationships = {}

                for row in fk_result.rows:
                    constraint_name = row[0]
                    column_name = row[1]
                    referenced_table = row[2]
                    referenced_column = row[3]

                    if constraint_name not in relationships:
                        relationships[constraint_name] = {
                            "referenced_table": referenced_table,
                            "local_columns": [],
                            "referenced_columns": [],
                        }

                    relationships[constraint_name]["local_columns"].append(column_name)
                    relationships[constraint_name]["referenced_columns"].append(
                        referenced_column
                    )

                result["foreign_keys"] = relationships

            # Get tables that reference this table
            ref_query = f"""
                SELECT DISTINCT
                    table_name as referencing_table
                FROM information_schema.KEY_COLUMN_USAGE
                WHERE referenced_table_name = '{table_name}'
                AND table_schema = DATABASE()
                AND referenced_table_name IS NOT NULL
            """
            ref_result = await self.db_manager.execute_query(ref_query)

            if ref_result.has_results:
                result["referenced_by"] = [row[0] for row in ref_result.rows]

            # Analyze relationship strength
            result["relationship_graph"] = await self._analyze_relationship_strength(
                table_name, result
            )

        except Exception as e:
            logger.error(f"Error in relationship exploration: {e}")
            result["error"] = str(e)

        return result

    async def _explore_timeseries(
        self,
        table_name: str,
        time_column: Optional[str] = None,
        sample_size: int = 1000,
    ) -> Dict[str, Any]:
        """Time-series analysis for temporal data."""
        result: Dict[str, Any] = {
            "time_analysis": {},
            "trends": {},
            "seasonality": {},
            "forecasting": {},
        }

        try:
            # Auto-detect time column if not specified
            if not time_column:
                time_column = await self._detect_time_column(table_name)

            if not time_column:
                result["error"] = "No temporal column found for time-series analysis"
                return result

            # Build time-series query
            ts_query = f"""
                SELECT
                    DATE({time_column}) as date,
                    COUNT(*) as record_count
                FROM `{table_name}`
                WHERE {time_column} IS NOT NULL
                GROUP BY DATE({time_column})
                ORDER BY date
                LIMIT {sample_size}
            """
            ts_result = await self.db_manager.execute_query(ts_query)

            if ts_result.has_results:
                # Analyze trends
                result["time_analysis"] = self._analyze_time_trends(ts_result.rows)

                # Detect seasonality
                result["seasonality"] = self._detect_seasonality(ts_result.rows)

                # Basic forecasting
                result["forecasting"] = self._generate_forecast(ts_result.rows)

        except Exception as e:
            logger.error(f"Error in time-series exploration: {e}")
            result["error"] = str(e)

        return result

    async def _explore_comparative(
        self,
        table_name: str,
        group_by: Optional[List[str]] = None,
        sample_size: int = 1000,
    ) -> Dict[str, Any]:
        """Comparative analysis across different data segments."""
        result: Dict[str, Any] = {
            "comparisons": {},
            "segment_analysis": {},
            "statistical_tests": {},
            "visualization_data": {},
        }

        try:
            if not group_by:
                # Auto-detect categorical columns for comparison
                group_by = await self._detect_categorical_columns(table_name)

            if group_by:
                # Build comparative analysis
                comp_query = self._build_comparative_query(
                    table_name, group_by, sample_size
                )
                comp_result = await self.db_manager.execute_query(comp_query)

                if comp_result.has_results:
                    result["comparisons"] = self._analyze_comparisons(
                        comp_result.rows, group_by
                    )

                    # Generate visualization data
                    result["visualization_data"] = self._prepare_visualization_data(
                        comp_result.rows, group_by
                    )

        except Exception as e:
            logger.error(f"Error in comparative exploration: {e}")
            result["error"] = str(e)

        return result

    async def _explore_sampling(
        self, table_name: str, sample_size: int
    ) -> Dict[str, Any]:
        """Smart sampling strategies for data exploration."""
        result: Dict[str, Any] = {
            "random_sample": {},
            "stratified_sample": {},
            "systematic_sample": {},
            "cluster_sample": {},
            "sampling_quality": {},
        }

        try:
            # Random sampling
            random_query = (
                f"SELECT * FROM `{table_name}` ORDER BY RAND() LIMIT {sample_size}"
            )
            random_result = await self.db_manager.execute_query(random_query)
            if random_result.has_results:
                result["random_sample"] = {
                    "data": random_result.rows,
                    "columns": random_result.columns,
                }

            # Stratified sampling (if categorical columns exist)
            categorical_cols = await self._detect_categorical_columns(table_name)
            if categorical_cols:
                stratified_data = await self._stratified_sampling(
                    table_name, categorical_cols[0], sample_size
                )
                result["stratified_sample"] = stratified_data

            # Systematic sampling
            systematic_data = await self._systematic_sampling(table_name, sample_size)
            result["systematic_sample"] = systematic_data

            # Assess sampling quality
            result["sampling_quality"] = self._assess_sampling_quality(result)

        except Exception as e:
            logger.error(f"Error in sampling exploration: {e}")
            result["error"] = str(e)

        return result

    # Helper methods for pattern analysis, anomaly detection, etc.
    def _analyze_column_patterns(
        self, data: List[Any], col_name: str
    ) -> Dict[str, Any]:
        """Analyze patterns in a single column."""
        patterns: Dict[str, Any] = {
            "data_type": type(data[0]).__name__ if data else "unknown",
            "unique_values": len(set(str(x) for x in data)),
            "total_values": len(data),
            "null_count": sum(1 for x in data if x is None),
            "patterns_detected": [],
        }

        # Detect common patterns
        if patterns["data_type"] == "str":
            # Check for email patterns
            email_pattern = sum(1 for x in data if isinstance(x, str) and "@" in x)
            if email_pattern > len(data) * 0.1:
                patterns["patterns_detected"].append("email_addresses")

            # Check for phone patterns
            phone_pattern = sum(
                1
                for x in data
                if isinstance(x, str)
                and any(char.isdigit() for char in x)
                and ("(" in x or "-" in x or "+" in x)
            )
            if phone_pattern > len(data) * 0.1:
                patterns["patterns_detected"].append("phone_numbers")

        return patterns

    def _detect_anomalies(
        self, data: List[List[Any]], columns: List[str]
    ) -> Dict[str, Any]:
        """Detect anomalies in the dataset."""
        anomalies = {}

        for i, col_name in enumerate(columns):
            col_data = [
                row[i]
                for row in data
                if row[i] is not None and isinstance(row[i], (int, float))
            ]

            if len(col_data) > 10:  # Need minimum data for anomaly detection
                mean = sum(col_data) / len(col_data)
                std_dev = (
                    sum((x - mean) ** 2 for x in col_data) / len(col_data)
                ) ** 0.5

                # Find outliers
                outliers = []
                for j, value in enumerate(col_data):
                    if abs(value - mean) > self.anomaly_threshold * std_dev:
                        outliers.append(
                            {
                                "row_index": j,
                                "value": value,
                                "deviation": abs(value - mean) / std_dev,
                            }
                        )

                if outliers:
                    anomalies[col_name] = {
                        "outlier_count": len(outliers),
                        "outliers": outliers[:10],  # Limit to top 10
                        "mean": mean,
                        "std_dev": std_dev,
                    }

        return anomalies

    def _analyze_correlations(
        self, data: List[List[Any]], columns: List[str]
    ) -> Dict[str, Any]:
        """Analyze correlations between numeric columns."""
        correlations = {}

        # Find numeric columns
        numeric_cols = []
        for i, col_name in enumerate(columns):
            col_data = [
                row[i]
                for row in data
                if row[i] is not None and isinstance(row[i], (int, float))
            ]
            if len(col_data) > 10:
                numeric_cols.append((i, col_name, col_data))

        # Calculate correlations between pairs
        for i, (idx1, name1, data1) in enumerate(numeric_cols):
            for j, (idx2, name2, data2) in enumerate(numeric_cols[i + 1 :], i + 1):
                if len(data1) == len(data2):
                    correlation = self._calculate_correlation(data1, data2)
                    if abs(correlation) > 0.3:  # Only significant correlations
                        key = f"{name1}_vs_{name2}"
                        correlations[key] = {
                            "correlation": correlation,
                            "strength": "strong"
                            if abs(correlation) > 0.7
                            else "moderate"
                            if abs(correlation) > 0.5
                            else "weak",
                            "direction": "positive" if correlation > 0 else "negative",
                        }

        return correlations

    def _calculate_correlation(self, x: List[float], y: List[float]) -> float:
        """Calculate Pearson correlation coefficient."""
        n = len(x)
        if n != len(y) or n < 2:
            return 0.0

        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))
        sum_x2 = sum(xi**2 for xi in x)
        sum_y2 = sum(yi**2 for yi in y)

        numerator = n * sum_xy - sum_x * sum_y
        denominator = ((n * sum_x2 - sum_x**2) * (n * sum_y2 - sum_y**2)) ** 0.5

        return numerator / denominator if denominator != 0 else 0.0

    def _format_exploration_results(
        self, result: Dict[str, Any], exploration_type: str, table_info: Dict[str, Any]
    ) -> str:
        """Format exploration results as human-readable text."""
        output = []
        output.append("=" * 80)
        output.append(f"INTERACTIVE EXPLORATION: {exploration_type.upper()}")
        output.append(f"Table: {table_info['table_name']}")
        output.append(f"Total Rows: {table_info['total_rows']:,}")
        output.append("=" * 80)

        if "error" in result:
            output.append(f"❌ Error: {result['error']}")
            return "\n".join(output)

        # Format based on exploration type
        if exploration_type == "drilldown":
            output.extend(self._format_drilldown_results(result))
        elif exploration_type == "patterns":
            output.extend(self._format_patterns_results(result))
        elif exploration_type == "relationships":
            output.extend(self._format_relationships_results(result))
        elif exploration_type == "timeseries":
            output.extend(self._format_timeseries_results(result))
        elif exploration_type == "comparative":
            output.extend(self._format_comparative_results(result))
        elif exploration_type == "sampling":
            output.extend(self._format_sampling_results(result))

        return "\n".join(output)

    def _format_drilldown_results(self, result: Dict[str, Any]) -> List[str]:
        """Format drilldown exploration results."""
        output = []

        if result.get("sample_data"):
            output.append(f"\nSAMPLE DATA ({len(result['sample_data'])} records):")
            output.append("-" * 50)

        if result.get("aggregations"):
            output.append("\nAGGREGATIONS:")
            output.append("-" * 50)
            # Add aggregation formatting

        return output

    def _format_patterns_results(self, result: Dict[str, Any]) -> List[str]:
        """Format pattern exploration results."""
        output = []

        if result.get("patterns"):
            output.append("\nDATA PATTERNS:")
            output.append("-" * 50)
            for col, pattern in result["patterns"].items():
                output.append(f"Column: {col}")
                output.append(f"  Type: {pattern['data_type']}")
                output.append(f"  Unique Values: {pattern['unique_values']}")
                if pattern["patterns_detected"]:
                    output.append(
                        f"  Detected Patterns: {', '.join(pattern['patterns_detected'])}"
                    )
                output.append("")

        if result.get("anomalies"):
            output.append("\nANOMALIES DETECTED:")
            output.append("-" * 50)
            for col, anomaly in result["anomalies"].items():
                output.append(f"Column: {col} - {anomaly['outlier_count']} outliers")

        return output

    def _format_relationships_results(self, result: Dict[str, Any]) -> List[str]:
        """Format relationship exploration results."""
        output = []

        if result.get("foreign_keys"):
            output.append("\nFOREIGN KEY RELATIONSHIPS:")
            output.append("-" * 50)
            for constraint, details in result["foreign_keys"].items():
                output.append(f"Constraint: {constraint}")
                output.append(f"  References: {details['referenced_table']}")
                output.append(f"  Local: {', '.join(details['local_columns'])}")
                output.append(f"  Remote: {', '.join(details['referenced_columns'])}")
                output.append("")

        if result.get("referenced_by"):
            output.append("\nREFERENCED BY TABLES:")
            output.append("-" * 50)
            for table in result["referenced_by"]:
                output.append(f"  • {table}")

        return output

    def _format_timeseries_results(self, result: Dict[str, Any]) -> List[str]:
        """Format time-series exploration results."""
        output = []

        if result.get("time_analysis"):
            output.append("\nTIME-SERIES ANALYSIS:")
            output.append("-" * 50)
            # Add time-series formatting

        return output

    def _format_comparative_results(self, result: Dict[str, Any]) -> List[str]:
        """Format comparative exploration results."""
        output = []

        if result.get("comparisons"):
            output.append("\nCOMPARATIVE ANALYSIS:")
            output.append("-" * 50)
            # Add comparative formatting

        return output

    def _format_sampling_results(self, result: Dict[str, Any]) -> List[str]:
        """Format sampling exploration results."""
        output = []

        output.append("\nSAMPLING ANALYSIS:")
        output.append("-" * 50)

        for sample_type, data in result.items():
            if sample_type != "sampling_quality" and data:
                output.append(
                    f"  {sample_type.upper()}: {len(data.get('data', []))} records"
                )

        return output

    # Additional helper methods would be implemented here
    def _build_where_clause(self, filters: Optional[Dict[str, Any]]) -> str:
        """Build WHERE clause from filters."""
        if not filters:
            return ""

        conditions: List[str] = []
        for col, value in filters.items():
            if isinstance(value, str):
                conditions.append(f"`{col}` = '{value}'")
            else:
                conditions.append(f"`{col}` = {value}")

        return " AND ".join(conditions)

    def _build_aggregation_query(
        self, table_name: str, group_by: List[str], filters: Optional[Dict[str, Any]]
    ) -> str:
        """Build aggregation query."""
        columns = [f"`{col}`" for col in group_by]
        columns.append("COUNT(*) as record_count")

        query = f"SELECT {', '.join(columns)} FROM `{table_name}`"

        where_clause = self._build_where_clause(filters)
        if where_clause:
            query += f" WHERE {where_clause}"

        query += f" GROUP BY {', '.join([f'`{col}`' for col in group_by])}"
        return query

    async def _analyze_distributions(
        self, table_name: str, sample_size: int, filters: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze data distributions."""
        return {}  # Placeholder implementation

    async def _assess_data_quality(
        self, table_name: str, sample_size: int
    ) -> Dict[str, Any]:
        """Assess data quality metrics."""
        return {}  # Placeholder implementation

    async def _detect_time_column(self, table_name: str) -> Optional[str]:
        """Auto-detect temporal columns."""
        return None  # Placeholder implementation

    def _analyze_time_trends(self, time_data: List[List[Any]]) -> Dict[str, Any]:
        """Analyze time-series trends."""
        return {}  # Placeholder implementation

    def _detect_seasonality(self, time_data: List[List[Any]]) -> Dict[str, Any]:
        """Detect seasonal patterns."""
        return {}  # Placeholder implementation

    def _generate_forecast(self, time_data: List[List[Any]]) -> Dict[str, Any]:
        """Generate basic forecasting."""
        return {}  # Placeholder implementation

    async def _detect_categorical_columns(self, table_name: str) -> List[str]:
        """Detect categorical columns for analysis."""
        return []  # Placeholder implementation

    def _build_comparative_query(
        self, table_name: str, group_by: List[str], sample_size: int
    ) -> str:
        """Build comparative analysis query."""
        return f"SELECT * FROM `{table_name}` LIMIT {sample_size}"  # Placeholder

    def _analyze_comparisons(
        self, data: List[List[Any]], group_by: List[str]
    ) -> Dict[str, Any]:
        """Analyze comparative data."""
        return {}  # Placeholder implementation

    def _prepare_visualization_data(
        self, data: List[List[Any]], group_by: List[str]
    ) -> Dict[str, Any]:
        """Prepare data for visualization."""
        return {}  # Placeholder implementation

    async def _stratified_sampling(
        self, table_name: str, category_column: str, sample_size: int
    ) -> Dict[str, Any]:
        """Perform stratified sampling."""
        return {}  # Placeholder implementation

    async def _systematic_sampling(
        self, table_name: str, sample_size: int
    ) -> Dict[str, Any]:
        """Perform systematic sampling."""
        return {}  # Placeholder implementation

    def _assess_sampling_quality(self, samples: Dict[str, Any]) -> Dict[str, Any]:
        """Assess quality of different sampling methods."""
        return {}  # Placeholder implementation

    async def _analyze_relationship_strength(
        self, table_name: str, relationships: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze relationship strength and dependencies."""
        return {}  # Placeholder implementation


async def explore_interactive_tool(
    table_name: str,
    exploration_type: str = "drilldown",
    sample_size: int = 1000,
    filters: Optional[Dict[str, Any]] = None,
    group_by: Optional[List[str]] = None,
    order_by: Optional[str] = None,
    time_column: Optional[str] = None,
    db_manager=None,
    security_validator=None,
) -> str:
    """
    Interactive data exploration tool.

    Args:
        table_name: Target table to explore
        exploration_type: Type of exploration
        sample_size: Number of records to sample
        filters: Optional filters to apply
        group_by: Columns to group by
        order_by: Column to order by
        time_column: Time column for time-series analysis
        db_manager: Database manager instance
        security_validator: Security validator instance

    Returns:
        Exploration results as formatted text
    """
    try:
        logger.info(
            f"Interactive exploration of table: {table_name}, type: {exploration_type}"
        )

        if not db_manager or not security_validator:
            raise RuntimeError("Server not properly initialized")

        if not security_validator._is_valid_table_name(table_name):
            raise ValueError(f"Invalid table name: {table_name}")

        explorer = InteractiveExplorer(db_manager)
        return await explorer.explore_interactive(
            table_name=table_name,
            exploration_type=exploration_type,
            sample_size=sample_size,
            filters=filters,
            group_by=group_by,
            order_by=order_by,
            time_column=time_column,
        )

    except Exception as e:
        logger.error(f"Error in interactive exploration: {e}")
        return f"Error: {str(e)}"
