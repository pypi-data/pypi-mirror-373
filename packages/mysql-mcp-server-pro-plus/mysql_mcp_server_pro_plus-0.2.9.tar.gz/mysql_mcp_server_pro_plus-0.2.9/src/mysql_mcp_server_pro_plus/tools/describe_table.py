from typing import Any, Dict

from ..logger import logger


class EnhancedTableDescriptor:
    """Enhanced table descriptor with statistical insights."""

    def __init__(self, db_manager):
        self.db_manager = db_manager

    async def get_table_statistics(self, table_name: str) -> Dict[str, Any]:
        """Get comprehensive table statistics and insights."""
        stats = {
            "table_info": {},
            "column_statistics": {},
            "indexes": {},
            "relationships": {},
            "data_quality": {},
            "performance_insights": {},
        }

        try:
            # Basic table information
            stats["table_info"] = await self._get_basic_table_info(table_name)

            # Column statistics
            stats["column_statistics"] = await self._get_column_statistics(table_name)

            # Index information
            stats["indexes"] = await self._get_index_info(table_name)

            # Foreign key relationships
            stats["relationships"] = await self._get_relationships(table_name)

            # Data quality metrics
            stats["data_quality"] = await self._get_data_quality_metrics(table_name)

            # Performance insights
            stats["performance_insights"] = await self._get_performance_insights(
                table_name
            )

        except Exception as e:
            logger.error(f"Error gathering statistics for table {table_name}: {e}")
            stats["error"] = {"message": str(e)}

        return stats

    async def _get_basic_table_info(self, table_name: str) -> Dict[str, Any]:
        """Get basic table information."""
        info = {}

        try:
            # Get row count - Use estimated count from INFORMATION_SCHEMA for large tables
            # to avoid expensive COUNT(*) operations
            estimated_count_query = f"""
                SELECT table_rows
                FROM information_schema.TABLES
                WHERE table_name = '{table_name}'
                AND table_schema = DATABASE()
            """
            estimated_result = await self.db_manager.execute_query(
                estimated_count_query
            )
            if estimated_result.has_results and estimated_result.rows[0][0] is not None:
                estimated_rows = estimated_result.rows[0][0]
                info["total_rows"] = estimated_rows
                info["row_count_method"] = "estimated_from_information_schema"

                # Only do exact count for small tables (< 100K rows)
                if estimated_rows <= 10000:
                    count_query = f"SELECT COUNT(*) as total_rows FROM `{table_name}`"
                    count_result = await self.db_manager.execute_query(count_query)
                    if count_result.has_results:
                        exact_count = count_result.rows[0][0]
                        info["total_rows"] = exact_count
                        info["row_count_method"] = "exact_count"
                        info["estimation_accuracy"] = "exact"
                    else:
                        info["row_count_method"] = "estimated_only"
            else:
                # Fallback to exact count if INFORMATION_SCHEMA doesn't have the data
                count_query = f"SELECT COUNT(*) as total_rows FROM `{table_name}`"
                count_result = await self.db_manager.execute_query(count_query)
                if count_result.has_results:
                    info["total_rows"] = count_result.rows[0][0]
                    info["row_count_method"] = "exact_count_fallback"

            # Get table size information
            size_query = f"""
                SELECT
                    data_length + index_length as total_size_bytes,
                    table_rows,
                    avg_row_length,
                    data_free
                FROM information_schema.TABLES
                WHERE table_name = '{table_name}'
                AND table_schema = DATABASE()
            """
            size_result = await self.db_manager.execute_query(size_query)
            if size_result.has_results:
                row = size_result.rows[0]
                info["total_size_bytes"] = row[0]
                info["estimated_rows"] = row[1]
                info["avg_row_length"] = row[2]
                info["data_free_bytes"] = row[3]

                # Convert to readable format
                if row[0]:
                    info["total_size_readable"] = self._format_bytes(row[0])

        except Exception as e:
            logger.warning(f"Error getting basic table info: {e}")

        return info

    async def _get_column_statistics(self, table_name: str) -> Dict[str, Any]:
        """Get detailed column statistics."""
        stats = {}

        try:
            # Get column information with statistics
            describe_query = f"DESCRIBE `{table_name}`"
            describe_result = await self.db_manager.execute_query(describe_query)

            if describe_result.has_results:
                for row in describe_result.rows:
                    col_name = row[0]
                    col_type = row[1]
                    nullable = row[2]
                    key = row[3]
                    default_val = row[4]
                    extra = row[5]

                    col_stats = {
                        "data_type": col_type,
                        "nullable": nullable == "YES",
                        "key_type": key,
                        "default_value": default_val,
                        "extra": extra,
                    }

                    # Get additional statistics for this column
                    try:
                        # Null count
                        null_query = f"SELECT COUNT(*) FROM `{table_name}` WHERE `{col_name}` IS NULL"
                        null_result = await self.db_manager.execute_query(null_query)
                        if null_result.has_results:
                            null_count = null_result.rows[0][0]
                            col_stats["null_count"] = null_count

                        # Unique values count (for smaller tables only)
                        table_info = await self._get_basic_table_info(table_name)
                        total_rows = table_info.get("total_rows", 0)

                        # Be more conservative with unique counts - only for very small tables
                        if total_rows <= 25000 and total_rows > 0:
                            unique_query = f"SELECT COUNT(DISTINCT `{col_name}`) FROM `{table_name}` WHERE `{col_name}` IS NOT NULL"
                            unique_result = await self.db_manager.execute_query(
                                unique_query
                            )
                            if unique_result.has_results:
                                unique_count = unique_result.rows[0][0]
                                col_stats["unique_count"] = unique_count
                                col_stats["uniqueness_ratio"] = unique_count / max(
                                    total_rows - null_count, 1
                                )

                        # Min/Max values for numeric columns
                        if any(
                            keyword in col_type.upper()
                            for keyword in ["INT", "DECIMAL", "FLOAT", "DOUBLE"]
                        ):
                            min_max_query = f"SELECT MIN(`{col_name}`), MAX(`{col_name}`) FROM `{table_name}` WHERE `{col_name}` IS NOT NULL"
                            min_max_result = await self.db_manager.execute_query(
                                min_max_query
                            )
                            if (
                                min_max_result.has_results
                                and min_max_result.rows[0][0] is not None
                            ):
                                col_stats["min_value"] = min_max_result.rows[0][0]
                                col_stats["max_value"] = min_max_result.rows[0][1]

                        # Most frequent values (top 5) - Very conservative threshold
                        if (
                            total_rows <= 15000 and total_rows > 0
                        ):  # Only for very small tables
                            freq_query = f"""
                                SELECT `{col_name}`, COUNT(*) as count
                                FROM `{table_name}`
                                WHERE `{col_name}` IS NOT NULL
                                GROUP BY `{col_name}`
                                ORDER BY count DESC
                                LIMIT 5
                            """
                            freq_result = await self.db_manager.execute_query(
                                freq_query
                            )
                            if freq_result.has_results:
                                frequent_values = []
                                for freq_row in freq_result.rows:
                                    frequent_values.append(
                                        {
                                            "value": str(freq_row[0]),
                                            "count": freq_row[1],
                                            "percentage": round(
                                                freq_row[1]
                                                / max(total_rows - null_count, 1)
                                                * 100,
                                                2,
                                            ),
                                        }
                                    )
                                col_stats["most_frequent_values"] = frequent_values

                    except Exception as e:
                        logger.warning(
                            f"Error getting statistics for column {col_name}: {e}"
                        )

                    stats[col_name] = col_stats

        except Exception as e:
            logger.error(f"Error getting column statistics: {e}")

        return stats

    async def _get_index_info(self, table_name: str) -> Dict[str, Any]:
        """Get index information for the table."""
        indexes = {}

        try:
            index_query = f"""
                SELECT
                    index_name,
                    column_name,
                    seq_in_index,
                    non_unique,
                    index_type
                FROM information_schema.STATISTICS
                WHERE table_name = '{table_name}'
                AND table_schema = DATABASE()
                ORDER BY index_name, seq_in_index
            """
            index_result = await self.db_manager.execute_query(index_query)

            if index_result.has_results:
                current_index = None
                current_columns = []

                for row in index_result.rows:
                    index_name = row[0]
                    column_name = row[1]
                    non_unique = row[3]
                    index_type = row[4]

                    if index_name != current_index:
                        if current_index:
                            indexes[current_index]["columns"] = current_columns

                        current_index = index_name
                        indexes[index_name] = {
                            "type": index_type,
                            "unique": not non_unique,
                            "columns": [],
                        }
                        current_columns = []

                    current_columns.append(column_name)

                # Add the last index
                if current_index:
                    indexes[current_index]["columns"] = current_columns

        except Exception as e:
            logger.warning(f"Error getting index information: {e}")

        return indexes

    async def _get_relationships(self, table_name: str) -> Dict[str, Any]:
        """Get foreign key relationships for the table."""
        relationships = {"foreign_keys": [], "referenced_by": []}

        try:
            # Foreign keys where this table is the child
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
                current_constraint = None
                current_fk: Dict[str, Any] = {}

                for row in fk_result.rows:
                    constraint_name = row[0]
                    column_name = row[1]
                    referenced_table = row[2]
                    referenced_column = row[3]

                    if constraint_name != current_constraint:
                        if current_fk is not None:
                            relationships["foreign_keys"].append(current_fk)

                        current_constraint = constraint_name
                        current_fk = {
                            "constraint_name": constraint_name,
                            "referenced_table": referenced_table,
                            "columns": [],
                            "referenced_columns": [],
                        }

                    if current_fk is not None:
                        current_fk["columns"].append(column_name)
                        current_fk["referenced_columns"].append(referenced_column)

                # Add the last foreign key
                if current_fk is not None:
                    relationships["foreign_keys"].append(current_fk)

            # Tables that reference this table
            ref_query = f"""
                SELECT DISTINCT
                    referenced_table_name as referencing_table,
                    table_name as referenced_table
                FROM information_schema.KEY_COLUMN_USAGE
                WHERE referenced_table_name = '{table_name}'
                AND table_schema = DATABASE()
                AND referenced_table_name IS NOT NULL
            """
            ref_result = await self.db_manager.execute_query(ref_query)

            if ref_result.has_results:
                relationships["referenced_by"] = [row[0] for row in ref_result.rows]

        except Exception as e:
            logger.warning(f"Error getting relationship information: {e}")

        return relationships

    async def _get_data_quality_metrics(self, table_name: str) -> Dict[str, Any]:
        """Get data quality metrics for the table."""
        quality = {}

        try:
            table_info = await self._get_basic_table_info(table_name)
            total_rows = table_info.get("total_rows", 0)

            if total_rows > 0:
                quality["total_rows"] = total_rows

                # Calculate null percentages for each column
                column_stats = await self._get_column_statistics(table_name)
                null_percentages = {}
                completeness_scores = {}

                for col_name, stats in column_stats.items():
                    null_count = stats.get("null_count", 0)
                    if null_count is not None:
                        null_percentage = (null_count / total_rows) * 100
                        null_percentages[col_name] = round(null_percentage, 2)
                        completeness_scores[col_name] = round(100 - null_percentage, 2)

                quality["null_percentages"] = null_percentages
                quality["completeness_scores"] = completeness_scores

                # Overall data quality score
                avg_completeness = (
                    sum(completeness_scores.values()) / len(completeness_scores)
                    if completeness_scores
                    else 100.0
                )
                quality["overall_quality_score"] = round(avg_completeness, 2)

                # Data quality insights
                insights = []
                for col_name, score in completeness_scores.items():
                    if score < 80:
                        insights.append(
                            f"Column '{col_name}' has low completeness ({score}%)"
                        )
                    elif score < 95:
                        insights.append(
                            f"Column '{col_name}' has moderate completeness ({score}%)"
                        )

                quality["quality_insights"] = insights

        except Exception as e:
            logger.warning(f"Error calculating data quality metrics: {e}")

        return quality

    async def _get_performance_insights(self, table_name: str) -> Dict[str, Any]:
        """Get performance-related insights for the table."""
        insights: Dict[str, Any] = {
            "primary_key_columns": [],
            "indexed_columns": [],
            "unindexed_columns": [],
            "index_coverage_percentage": 0.0,
            "recommendations": [],
        }

        try:
            # Check for primary key
            pk_query = f"""
                SELECT column_name
                FROM information_schema.KEY_COLUMN_USAGE
                WHERE table_name = '{table_name}'
                AND table_schema = DATABASE()
                AND constraint_name = 'PRIMARY'
                ORDER BY ordinal_position
            """
            pk_result = await self.db_manager.execute_query(pk_query)

            if pk_result.has_results:
                insights["primary_key_columns"] = [row[0] for row in pk_result.rows]
            else:
                insights["recommendations"].append(
                    "Consider adding a primary key for better performance"
                )

            # Index coverage analysis
            index_info = await self._get_index_info(table_name)
            column_stats = await self._get_column_statistics(table_name)

            indexed_columns = set()
            for index_name, index_data in index_info.items():
                indexed_columns.update(index_data["columns"])

            all_columns = set(column_stats.keys())
            unindexed_columns = all_columns - indexed_columns

            insights["indexed_columns"] = list(indexed_columns)
            insights["unindexed_columns"] = list(unindexed_columns)
            insights["index_coverage_percentage"] = (
                round(len(indexed_columns) / len(all_columns) * 100, 2)
                if all_columns
                else 0.0
            )

            # Additional recommendations based on analysis
            if insights["index_coverage_percentage"] < 50:
                insights["recommendations"].append(
                    "Consider adding indexes on frequently queried columns"
                )

            # Check for potential performance issues
            table_info = await self._get_basic_table_info(table_name)
            data_free = table_info.get("data_free_bytes", 0)
            if data_free and data_free > 1024 * 1024:  # More than 1MB free space
                insights["recommendations"].append(
                    "Consider optimizing table to reclaim free space"
                )

        except Exception as e:
            logger.warning(f"Error getting performance insights: {e}")

        return insights

    def _format_bytes(self, bytes_value: int) -> str:
        """Format bytes into human readable format."""
        if bytes_value is None:
            return "N/A"

        value = float(bytes_value)
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if value < 1024.0:
                return ".2f"
            value /= 1024.0
        return ".2f"

    def format_statistics_as_text(self, stats: Dict[str, Any]) -> str:
        """Format statistics as machine-readable text for agents."""
        if "error" in stats:
            error_info = stats["error"]
            if isinstance(error_info, dict):
                return f"ERROR: {error_info.get('message', 'Unknown error')}"
            return f"ERROR: {error_info}"

        output = []

        # Basic table information
        table_info = stats.get("table_info", {})
        if table_info:
            output.append("TABLE_INFO:")
            for key, value in table_info.items():
                if key == "total_size_readable":
                    output.append(f"total_size:{value}")
                elif key == "total_rows":
                    row_count = str(value)
                    method = table_info.get("row_count_method", "")
                    if "estimated" in method:
                        row_count += "_estimated"
                    output.append(f"total_rows:{row_count}")
                elif key == "estimated_rows":
                    output.append(f"estimated_rows:{value}")
                elif key == "avg_row_length":
                    output.append(f"avg_row_length:{value}")
                elif key == "data_free_bytes" and value > 0:
                    output.append(f"free_space:{self._format_bytes(value)}")

            # Performance note for large tables
            total_rows = table_info.get("total_rows", 0)
            if total_rows > 100000:
                output.append(
                    "NOTE:Advanced statistics limited for large tables (>100K rows)"
                )

        # Column statistics
        column_stats = stats.get("column_statistics", {})
        if column_stats:
            output.append("COLUMNS:")
            total_rows = table_info.get("total_rows", 0)
            if total_rows > 25000:
                output.append(
                    f"NOTE:Detailed statistics limited for performance ({total_rows} rows >25K threshold)"
                )

            for col_name, col_data in column_stats.items():
                col_info = [f"name:{col_name}"]
                col_info.append(f"type:{col_data.get('data_type', 'N/A')}")
                col_info.append(f"nullable:{col_data.get('nullable', 'N/A')}")
                col_info.append(f"key:{col_data.get('key_type', 'N/A')}")

                if "null_count" in col_data:
                    col_info.append(f"null_count:{col_data['null_count']}")
                if "unique_count" in col_data:
                    col_info.append(f"unique_count:{col_data['unique_count']}")
                    if "uniqueness_ratio" in col_data:
                        col_info.append(
                            f"uniqueness_ratio:{col_data['uniqueness_ratio']:.4f}"
                        )

                if "min_value" in col_data and "max_value" in col_data:
                    col_info.append(
                        f"range:{col_data['min_value']}-{col_data['max_value']}"
                    )

                # Most frequent values
                frequent = col_data.get("most_frequent_values", [])
                if frequent:
                    freq_str = ";".join(
                        [
                            f"{val['value']}:{val['count']}:{val['percentage']:.2f}"
                            for val in frequent[:3]
                        ]
                    )
                    col_info.append(f"top_values:{freq_str}")

                output.append("|".join(col_info))

        # Index information
        indexes = stats.get("indexes", {})
        if indexes:
            output.append("INDEXES:")
            for index_name, index_data in indexes.items():
                index_info = [
                    f"name:{index_name}",
                    f"type:{index_data.get('type', 'N/A')}",
                    f"unique:{index_data.get('unique', 'N/A')}",
                    f"columns:{','.join(index_data.get('columns', []))}",
                ]
                output.append("|".join(index_info))

        # Relationships
        relationships = stats.get("relationships", {})
        if relationships:
            # Foreign keys
            foreign_keys = relationships.get("foreign_keys", [])
            if foreign_keys:
                output.append("FOREIGN_KEYS:")
                for fk in foreign_keys:
                    fk_info = [
                        f"constraint:{fk['constraint_name']}",
                        f"references:{fk['referenced_table']}",
                        f"local_cols:{','.join(fk['columns'])}",
                        f"ref_cols:{','.join(fk['referenced_columns'])}",
                    ]
                    output.append("|".join(fk_info))

            # Referenced by
            referenced_by = relationships.get("referenced_by", [])
            if referenced_by:
                output.append(f"REFERENCED_BY:{','.join(referenced_by)}")

        # Data quality
        data_quality = stats.get("data_quality", {})
        if data_quality:
            output.append("DATA_QUALITY:")
            quality_score = data_quality.get("overall_quality_score", 0)
            output.append(f"overall_score:{quality_score}")

            insights = data_quality.get("quality_insights", [])
            if insights:
                insight_str = ";".join(insights)
                output.append(f"insights:{insight_str}")

        # Performance insights
        perf_insights = stats.get("performance_insights", {})
        if perf_insights:
            output.append("PERFORMANCE:")
            coverage = perf_insights.get("index_coverage_percentage", 0)
            output.append(f"index_coverage:{coverage}")

            recommendations = perf_insights.get("recommendations", [])
            if recommendations:
                rec_str = ";".join(recommendations)
                output.append(f"recommendations:{rec_str}")

        return "\n".join(output)


async def describe_table_tool(table_name: str, db_manager, security_validator) -> str:
    """Enhanced table description with statistical insights.

    Args:
        table_name: Name of the table to describe
        db_manager: Database manager instance
        security_validator: Security validator instance
    """
    try:
        logger.info(f"Enhanced description of table: {table_name}")

        if not db_manager or not security_validator:
            raise RuntimeError("Server not properly initialized")

        if not security_validator._is_valid_table_name(table_name):
            raise ValueError(f"Invalid table name: {table_name}")

        # Create enhanced descriptor
        descriptor = EnhancedTableDescriptor(db_manager)

        # Get comprehensive statistics
        stats = await descriptor.get_table_statistics(table_name)

        # Format as readable text
        return descriptor.format_statistics_as_text(stats)

    except Exception as e:
        logger.error(f"Error describing table {table_name}: {e}")
        return f"Error: {str(e)}"


async def describe_table_basic_tool(
    table_name: str, db_manager, security_validator
) -> str:
    """Basic table description (original functionality).

    Args:
        table_name: Name of the table to describe
        db_manager: Database manager instance
        security_validator: Security validator instance
    """
    try:
        logger.info(f"Basic description of table: {table_name}")

        if not db_manager or not security_validator:
            raise RuntimeError("Server not properly initialized")

        if not security_validator._is_valid_table_name(table_name):
            raise ValueError(f"Invalid table name: {table_name}")

        query = f"DESCRIBE `{table_name}`"
        result = await db_manager.execute_query(query)

        if result.has_results:
            lines = [",".join(result.columns)]
            for row in result.rows:
                lines.append(",".join(str(cell) for cell in row))
            return "\n".join(lines)
        else:
            return "No table structure information available"

    except Exception as e:
        logger.error(f"Error describing table {table_name}: {e}")
        return f"Error: {str(e)}"
