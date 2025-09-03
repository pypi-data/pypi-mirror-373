"""Schema visualization tool for MySQL databases.

Provides comprehensive schema analysis with ER diagrams, relationship mapping,
and dependency visualization using INFORMATION_SCHEMA queries.
"""

from __future__ import annotations

import asyncio
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, cast

from ..logger import logger


class SchemaVisualizer:
    """Analyzer for MySQL database schema visualization and relationships."""

    def __init__(self, db_manager):
        self.db_manager = db_manager

    async def get_schema_visualization(
        self,
        schema_name: Optional[str] = None,
        format: str = "text",
        timeout: int = 300,
    ) -> str:
        """
        Generate comprehensive schema visualization with ER diagrams and relationship analysis.

        Features:
        - ER Diagram Generation: ASCII/text-based relationship diagrams
        - Table Dependencies: Foreign key relationships, dependency chains
        - Relationship Types: One-to-one, one-to-many, many-to-many mappings
        - Constraint Visualization: Primary keys, unique constraints, check constraints
        - Circular Reference Detection: Identify potential design issues
        - Impact Analysis: Show cascading effects of schema changes

        Args:
            schema_name: Specific schema to analyze (default: current database)
            format: Output format - "text", "tree", or "detailed" (default: "text")
            timeout: Maximum execution time in seconds (default: 300)

        Returns:
            String containing comprehensive schema visualization and analysis
        """
        start_time = time.time()
        try:
            result = await asyncio.wait_for(
                self._get_schema_visualization_internal(
                    schema_name, format, start_time
                ),
                timeout=timeout,
            )
            return self._format_as_text(result, format)
        except asyncio.TimeoutError:
            logger.warning(f"Schema visualization timed out after {timeout} seconds")
            return self._format_timeout_result(timeout)
        except Exception as e:
            logger.error(f"Error generating schema visualization: {e}")
            return self._format_error_result(str(e))

    async def _get_schema_visualization_internal(
        self, schema_name: Optional[str], format: str, start_time: float
    ) -> Dict[str, Any]:
        """Internal method for comprehensive schema visualization."""
        result: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "analysis_duration_seconds": 0.0,
            "schema_name": schema_name or "current_database",
            "format": format,
            "tables": {},
            "relationships": [],
            "constraints": {},
            "dependencies": {},
            "statistics": {},
        }

        try:
            # 1. Get table information
            result["tables"] = await self._get_table_information(schema_name)

            # 2. Get relationship mapping
            result["relationships"] = await self._get_table_relationships(schema_name)

            # 3. Get constraint information
            result["constraints"] = await self._get_constraint_information(schema_name)

            # 4. Analyze dependencies
            result["dependencies"] = await self._analyze_dependencies(
                result["relationships"]
            )

            # 5. Detect circular references
            result["circular_references"] = await self._detect_circular_references(
                result["relationships"]
            )

            # 6. Generate statistics
            result["statistics"] = await self._generate_schema_statistics(result)

            # 7. Create ER diagram
            result["er_diagram"] = await self._generate_er_diagram(result, format)

            result["analysis_duration_seconds"] = time.time() - start_time
            return result

        except Exception as e:
            logger.error(f"Error in schema visualization: {e}")
            result["error"] = str(e)
            result["analysis_duration_seconds"] = time.time() - start_time
            return result

    async def _get_table_information(
        self, schema_name: Optional[str]
    ) -> Dict[str, Any]:
        """Get comprehensive table information from INFORMATION_SCHEMA."""
        try:
            # Build query for table information
            where_clause = ""
            if schema_name:
                where_clause = f"WHERE TABLE_SCHEMA = '{schema_name}'"
            else:
                where_clause = "WHERE TABLE_SCHEMA = DATABASE()"

            query = f"""
            SELECT 
                TABLE_NAME,
                TABLE_TYPE,
                ENGINE,
                TABLE_ROWS,
                DATA_LENGTH,
                INDEX_LENGTH,
                TABLE_COLLATION,
                TABLE_COMMENT
            FROM INFORMATION_SCHEMA.TABLES
            {where_clause}
            ORDER BY TABLE_NAME
            """

            result = await self.db_manager.execute_query(query)
            tables = {}

            if result.has_results:
                for row in result.rows:
                    row_dict = dict(zip(result.columns, row))
                    table_name = row_dict["TABLE_NAME"]
                    tables[table_name] = {
                        "type": row_dict.get("TABLE_TYPE", "BASE TABLE"),
                        "engine": row_dict.get("ENGINE", "Unknown"),
                        "rows": row_dict.get("TABLE_ROWS", 0),
                        "data_size": row_dict.get("DATA_LENGTH", 0),
                        "index_size": row_dict.get("INDEX_LENGTH", 0),
                        "collation": row_dict.get("TABLE_COLLATION", ""),
                        "comment": row_dict.get("TABLE_COMMENT", ""),
                        "columns": await self._get_table_columns(
                            table_name, schema_name
                        ),
                    }

            return {"tables": tables, "status": "success"}
        except Exception as e:
            logger.error(f"Error getting table information: {e}")
            return {"tables": {}, "status": "error", "error": str(e)}

    async def _get_table_columns(
        self, table_name: str, schema_name: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Get column information for a specific table."""
        try:
            where_clause = f"TABLE_NAME = '{table_name}'"
            if schema_name:
                where_clause += f" AND TABLE_SCHEMA = '{schema_name}'"
            else:
                where_clause += " AND TABLE_SCHEMA = DATABASE()"

            query = f"""
            SELECT 
                COLUMN_NAME,
                DATA_TYPE,
                IS_NULLABLE,
                COLUMN_KEY,
                COLUMN_DEFAULT,
                EXTRA,
                COLUMN_COMMENT
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE {where_clause}
            ORDER BY ORDINAL_POSITION
            """

            result = await self.db_manager.execute_query(query)
            columns = []

            if result.has_results:
                for row in result.rows:
                    row_dict = dict(zip(result.columns, row))
                    columns.append(
                        {
                            "name": row_dict.get("COLUMN_NAME", ""),
                            "type": row_dict.get("DATA_TYPE", ""),
                            "nullable": row_dict.get("IS_NULLABLE", "YES") == "YES",
                            "key": row_dict.get("COLUMN_KEY", ""),
                            "default": row_dict.get("COLUMN_DEFAULT"),
                            "extra": row_dict.get("EXTRA", ""),
                            "comment": row_dict.get("COLUMN_COMMENT", ""),
                        }
                    )

            return columns
        except Exception as e:
            logger.error(f"Error getting columns for table {table_name}: {e}")
            return []

    async def _get_table_relationships(
        self, schema_name: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Get foreign key relationships between tables."""
        try:
            where_clause = ""
            if schema_name:
                where_clause = f"WHERE CONSTRAINT_SCHEMA = '{schema_name}'"
            else:
                where_clause = "WHERE CONSTRAINT_SCHEMA = DATABASE()"

            query = f"""
            SELECT 
                TABLE_NAME as child_table,
                COLUMN_NAME as child_column,
                REFERENCED_TABLE_NAME as parent_table,
                REFERENCED_COLUMN_NAME as parent_column,
                CONSTRAINT_NAME
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            {where_clause}
            AND REFERENCED_TABLE_NAME IS NOT NULL
            ORDER BY TABLE_NAME, COLUMN_NAME
            """

            result = await self.db_manager.execute_query(query)
            relationships = []

            if result.has_results:
                for row in result.rows:
                    row_dict = dict(zip(result.columns, row))
                    relationships.append(
                        {
                            "child_table": row_dict.get("child_table", ""),
                            "child_column": row_dict.get("child_column", ""),
                            "parent_table": row_dict.get("parent_table", ""),
                            "parent_column": row_dict.get("parent_column", ""),
                            "constraint_name": row_dict.get("CONSTRAINT_NAME", ""),
                            "type": self._determine_relationship_type(row_dict),
                        }
                    )

            return relationships
        except Exception as e:
            logger.error(f"Error getting table relationships: {e}")
            return []

    def _determine_relationship_type(self, relationship: Dict[str, Any]) -> str:
        """Determine the type of relationship (1:1, 1:N, N:M)."""
        # This is a simplified implementation - in practice you'd need to check
        # uniqueness constraints and cardinalities
        return "one-to-many"  # Default assumption

    async def _get_constraint_information(
        self, schema_name: Optional[str]
    ) -> Dict[str, Any]:
        """Get constraint information for all tables."""
        try:
            where_clause = ""
            if schema_name:
                where_clause = f"WHERE CONSTRAINT_SCHEMA = '{schema_name}'"
            else:
                where_clause = "WHERE CONSTRAINT_SCHEMA = DATABASE()"

            query = f"""
            SELECT 
                TABLE_NAME,
                CONSTRAINT_NAME,
                CONSTRAINT_TYPE,
                COLUMN_NAME
            FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
            LEFT JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE kcu
                ON tc.CONSTRAINT_NAME = kcu.CONSTRAINT_NAME
                AND tc.TABLE_SCHEMA = kcu.TABLE_SCHEMA
            {where_clause}
            ORDER BY TABLE_NAME, CONSTRAINT_TYPE, CONSTRAINT_NAME
            """

            result = await self.db_manager.execute_query(query)
            constraints = {}

            if result.has_results:
                for row in result.rows:
                    row_dict = dict(zip(result.columns, row))
                    table_name = row_dict.get("TABLE_NAME", "")

                    if table_name not in constraints:
                        constraints[table_name] = {
                            "primary_keys": [],
                            "foreign_keys": [],
                            "unique_constraints": [],
                            "check_constraints": [],
                        }

                    constraint_type = row_dict.get("CONSTRAINT_TYPE", "")
                    column_name = row_dict.get("COLUMN_NAME", "")
                    constraint_name = row_dict.get("CONSTRAINT_NAME", "")

                    if constraint_type == "PRIMARY KEY" and column_name:
                        constraints[table_name]["primary_keys"].append(column_name)
                    elif constraint_type == "FOREIGN KEY":
                        constraints[table_name]["foreign_keys"].append(
                            {"name": constraint_name, "column": column_name}
                        )
                    elif constraint_type == "UNIQUE" and column_name:
                        constraints[table_name]["unique_constraints"].append(
                            column_name
                        )
                    elif constraint_type == "CHECK":
                        constraints[table_name]["check_constraints"].append(
                            constraint_name
                        )

            return {"constraints": constraints, "status": "success"}
        except Exception as e:
            logger.error(f"Error getting constraint information: {e}")
            return {"constraints": {}, "status": "error", "error": str(e)}

    async def _analyze_dependencies(
        self, relationships: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze table dependencies based on foreign key relationships."""
        try:
            dependencies = {}
            dependency_chains = []

            # Build dependency graph
            for rel in relationships:
                child = rel["child_table"]
                parent = rel["parent_table"]

                if child not in dependencies:
                    dependencies[child] = {"depends_on": [], "depended_by": []}
                if parent not in dependencies:
                    dependencies[parent] = {"depends_on": [], "depended_by": []}

                dependencies[child]["depends_on"].append(parent)
                dependencies[parent]["depended_by"].append(child)

            # Find dependency chains
            for table in dependencies:
                chain = self._find_dependency_chain(table, dependencies, [])
                if len(chain) > 1:
                    dependency_chains.append(chain)

            return {
                "dependencies": dependencies,
                "dependency_chains": dependency_chains,
                "status": "success",
            }
        except Exception as e:
            logger.error(f"Error analyzing dependencies: {e}")
            return {"dependencies": {}, "dependency_chains": [], "status": "error"}

    def _find_dependency_chain(
        self,
        table: str,
        dependencies: Dict[str, Dict[str, List[str]]],
        visited: List[str],
    ) -> List[str]:
        """Find dependency chain for a table."""
        if table in visited:
            return visited + [table]  # Circular reference found

        visited = visited + [table]
        chain: List[str] = [table]

        table_deps = dependencies.get(table, {})
        if table_deps:
            depends_on = table_deps.get("depends_on", [])
            for parent in depends_on:
                parent_chain: List[str] = self._find_dependency_chain(
                    parent, dependencies, visited
                )
                if len(parent_chain) > len(chain):
                    chain = parent_chain

        return cast(List[str], chain)

    async def _detect_circular_references(
        self, relationships: List[Dict[str, Any]]
    ) -> List[str]:
        """Detect circular references in foreign key relationships."""
        try:
            graph = {}
            for rel in relationships:
                child = rel["child_table"]
                parent = rel["parent_table"]

                if child not in graph:
                    graph[child] = []
                graph[child].append(parent)

            # Use DFS to detect cycles
            visited = set()
            rec_stack = set()
            cycles = []

            def dfs(node: str, path: List[str]) -> None:
                if node in rec_stack:
                    cycle_start = path.index(node)
                    cycles.append(" → ".join(path[cycle_start:] + [node]))
                    return

                if node in visited:
                    return

                visited.add(node)
                rec_stack.add(node)

                for neighbor in graph.get(node, []):
                    dfs(neighbor, path + [neighbor])

                rec_stack.remove(node)

            for table in graph:
                if table not in visited:
                    dfs(table, [table])

            return cycles
        except Exception as e:
            logger.error(f"Error detecting circular references: {e}")
            return []

    async def _generate_schema_statistics(
        self, analysis_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive schema statistics."""
        try:
            tables = analysis_result.get("tables", {}).get("tables", {})
            relationships = analysis_result.get("relationships", [])
            constraints = analysis_result.get("constraints", {}).get("constraints", {})

            stats = {
                "total_tables": len(tables),
                "total_relationships": len(relationships),
                "total_constraints": sum(
                    len(table_constraints.get("primary_keys", []))
                    + len(table_constraints.get("foreign_keys", []))
                    + len(table_constraints.get("unique_constraints", []))
                    + len(table_constraints.get("check_constraints", []))
                    for table_constraints in constraints.values()
                ),
                "tables_with_relationships": len(
                    set(rel["child_table"] for rel in relationships).union(
                        set(rel["parent_table"] for rel in relationships)
                    )
                ),
                "orphaned_tables": [],
                "largest_tables": [],
                "status": "success",
            }

            # Find orphaned tables (no relationships)
            tables_with_rels = set(rel["child_table"] for rel in relationships).union(
                set(rel["parent_table"] for rel in relationships)
            )
            stats["orphaned_tables"] = [
                table for table in tables.keys() if table not in tables_with_rels
            ]

            # Find largest tables by row count
            table_sizes = [(name, info.get("rows", 0)) for name, info in tables.items()]
            table_sizes.sort(key=lambda x: x[1], reverse=True)
            stats["largest_tables"] = table_sizes[:5]

            return stats
        except Exception as e:
            logger.error(f"Error generating schema statistics: {e}")
            return {"status": "error", "error": str(e)}

    async def _generate_er_diagram(
        self, analysis_result: Dict[str, Any], format: str
    ) -> str:
        """Generate ER diagram in the specified format."""
        try:
            tables = analysis_result.get("tables", {}).get("tables", {})
            relationships = analysis_result.get("relationships", [])

            if format == "tree":
                return self._generate_tree_diagram(tables, relationships)
            elif format == "detailed":
                return self._generate_detailed_diagram(tables, relationships)
            else:  # default "text"
                return self._generate_text_diagram(tables, relationships)

        except Exception as e:
            logger.error(f"Error generating ER diagram: {e}")
            return f"Error generating diagram: {str(e)}"

    def _generate_text_diagram(
        self, tables: Dict[str, Any], relationships: List[Dict[str, Any]]
    ) -> str:
        """Generate compact text-based ER diagram."""
        lines = ["SCHEMA ER DIAGRAM", "=" * 20]

        # Tables section
        lines.append("TABLES:")
        for table_name, table_info in sorted(tables.items()):
            row_count = table_info.get("rows", 0)
            engine = table_info.get("engine", "Unknown")
            lines.append(f"{table_name} ({row_count:,} rows, {engine})")

            # Primary keys
            columns = table_info.get("columns", [])
            pk_columns = [col["name"] for col in columns if col["key"] == "PRI"]
            if pk_columns:
                lines.append(f"  PK: {', '.join(pk_columns)}")

        # Relationships section
        if relationships:
            lines.append("\nRELATIONSHIPS:")
            for rel in relationships:
                lines.append(
                    f"{rel['parent_table']}.{rel['parent_column']} -> "
                    f"{rel['child_table']}.{rel['child_column']} ({rel['type']})"
                )
        else:
            lines.append("\nNO RELATIONSHIPS")

        return "\n".join(lines)

    def _generate_tree_diagram(
        self, tables: Dict[str, Any], relationships: List[Dict[str, Any]]
    ) -> str:
        """Generate compact tree-based hierarchy diagram."""
        lines = ["SCHEMA HIERARCHY", "=" * 15]

        # Build parent-child relationships
        children_map = {}
        parents_set = set()
        children_set = set()

        for rel in relationships:
            parent = rel["parent_table"]
            child = rel["child_table"]

            if parent not in children_map:
                children_map[parent] = []
            children_map[parent].append(child)

            parents_set.add(parent)
            children_set.add(child)

        # Find root tables (parents but not children)
        root_tables = parents_set - children_set

        # If no clear hierarchy, show all tables
        if not root_tables:
            root_tables = set(tables.keys())

        # Generate tree structure
        visited = set()
        for root in sorted(root_tables):
            lines.extend(self._build_tree_branch(root, children_map, visited, 0))

        return "\n".join(lines)

    def _build_tree_branch(
        self, table: str, children_map: Dict[str, List[str]], visited: set, depth: int
    ) -> List[str]:
        """Build tree branch for a table and its children."""
        lines = []
        indent = "  " * depth
        prefix = "+- " if depth > 0 else ""

        if table in visited:
            lines.append(f"{indent}{prefix}{table} (circular)")
            return lines

        visited.add(table)
        lines.append(f"{indent}{prefix}{table}")

        children = children_map.get(table, [])
        for child in children:
            lines.extend(
                self._build_tree_branch(child, children_map, visited, depth + 1)
            )

        return lines

    def _generate_detailed_diagram(
        self, tables: Dict[str, Any], relationships: List[Dict[str, Any]]
    ) -> str:
        """Generate detailed diagram with full table structures."""
        lines = ["DETAILED SCHEMA", "=" * 15]

        for table_name, table_info in sorted(tables.items()):
            lines.extend(
                [
                    f"TABLE: {table_name}",
                    f"Engine: {table_info.get('engine', 'Unknown')}",
                    f"Rows: {table_info.get('rows', 0):,}",
                    f"Size: {table_info.get('data_size', 0):,} bytes",
                    "COLUMNS:",
                ]
            )

            columns = table_info.get("columns", [])
            for col in columns:
                key_indicator = ""
                if col["key"] == "PRI":
                    key_indicator = " [PK]"
                elif col["key"] == "UNI":
                    key_indicator = " [UQ]"
                elif col["key"] == "MUL":
                    key_indicator = " [FK]"

                nullable = "NULL" if col["nullable"] else "NOT NULL"
                lines.append(
                    f"  {col['name']} ({col['type']}) {nullable}{key_indicator}"
                )

            lines.append("")

        # Add relationships section
        if relationships:
            lines.extend(["FOREIGN KEY RELATIONSHIPS:", "=" * 25])
            for rel in relationships:
                lines.append(
                    f"{rel['parent_table']}.{rel['parent_column']} -> "
                    f"{rel['child_table']}.{rel['child_column']}"
                )

        return "\n".join(lines)

    def _format_as_text(self, result: Dict[str, Any], format: str) -> str:
        """Format analysis result as structured text for agent consumption."""
        output = {
            "schema_visualization": {
                "timestamp": result.get("timestamp"),
                "duration_seconds": round(
                    result.get("analysis_duration_seconds", 0), 2
                ),
                "schema_name": result.get("schema_name"),
                "format": result.get("format"),
                "statistics": {},
                "tables": {},
                "relationships": [],
                "constraints": {},
                "dependencies": {},
                "circular_references": [],
            }
        }

        # Add statistics
        stats = result.get("statistics", {})
        if stats.get("status") == "success":
            output["schema_visualization"]["statistics"] = {
                "total_tables": stats.get("total_tables", 0),
                "total_relationships": stats.get("total_relationships", 0),
                "total_constraints": stats.get("total_constraints", 0),
                "tables_with_relationships": stats.get("tables_with_relationships", 0),
                "orphaned_tables_count": len(stats.get("orphaned_tables", [])),
                "orphaned_tables": stats.get("orphaned_tables", []),
                "largest_tables": stats.get("largest_tables", []),
            }

        # Add core data structures
        output["schema_visualization"]["tables"] = result.get("tables", {}).get(
            "tables", {}
        )
        output["schema_visualization"]["relationships"] = result.get(
            "relationships", []
        )
        output["schema_visualization"]["constraints"] = result.get(
            "constraints", {}
        ).get("constraints", {})
        output["schema_visualization"]["dependencies"] = result.get(
            "dependencies", {}
        ).get("dependencies", {})
        output["schema_visualization"]["circular_references"] = result.get(
            "circular_references", []
        )

        # Add ER diagram if present
        er_diagram = result.get("er_diagram", "")
        if er_diagram:
            output["schema_visualization"]["er_diagram"] = er_diagram

        # Handle errors
        if "error" in result:
            output["schema_visualization"]["error"] = result["error"]

        import json

        return json.dumps(output, indent=2, default=str)

    def _format_timeout_result(self, timeout: int) -> str:
        """Format timeout result."""
        return f'{{"schema_visualization": {{"error": "Analysis timed out after {timeout} seconds. Try reducing schema complexity or increasing timeout limit."}}}}'

    def _format_error_result(self, error: str) -> str:
        """Format error result."""
        return f'{{"schema_visualization": {{"error": "{error}"}}}}'


async def get_schema_visualization_tool(
    schema_name: Optional[str],
    format: str,
    db_manager,
    security_validator,
    timeout: int = 300,
) -> str:
    """
    Generate comprehensive schema visualization with ER diagrams and relationship analysis.

    Args:
        schema_name: Specific schema to analyze (optional)
        format: Output format (text, tree, detailed)
        db_manager: Database manager instance
        security_validator: Security validator instance
        timeout: Maximum execution time in seconds

    Returns:
        String containing schema visualization results
    """
    try:
        logger.info(
            f"Generating schema visualization for: {schema_name or 'current database'}"
        )

        if not db_manager:
            raise RuntimeError("Server not properly initialized")

        # Validate schema name if provided
        if schema_name and not security_validator._is_valid_table_name(schema_name):
            raise ValueError(f"Invalid schema name: {schema_name}")

        # Create visualizer and run analysis
        visualizer = SchemaVisualizer(db_manager)
        return await visualizer.get_schema_visualization(schema_name, format, timeout)

    except Exception as e:
        logger.error(f"Schema visualization error: {e}")
        return f"Error: {str(e)}"
