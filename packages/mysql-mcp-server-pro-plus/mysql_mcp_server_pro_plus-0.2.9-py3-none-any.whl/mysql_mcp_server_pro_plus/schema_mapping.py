"""Schema mapping tool for MySQL database relationship analysis.

Adapted for MySQL from the original postgres-mcp project.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class SchemaMappingTool:
    """Tool for analyzing schema relationships in MySQL databases."""

    def __init__(self, db_manager):
        self.db_manager = db_manager

    async def analyze_schema_relationships(self, schemas: List[str]) -> str:
        """Analyze relationships between schemas in MySQL.

        Args:
            schemas: List of schema names to analyze

        Returns:
            Formatted text analysis of schema relationships
        """
        try:
            logger.info(f"Analyzing relationships for {len(schemas)} schemas")

            # Get cross-schema relationships
            cross_schema_relationships = await self._get_cross_schema_relationships(
                schemas
            )

            # Analyze schema connectivity
            schema_connectivity = await self._analyze_schema_connectivity(
                schemas, cross_schema_relationships
            )

            # Generate analysis text
            return self._format_schema_analysis(
                schemas, cross_schema_relationships, schema_connectivity
            )

        except Exception as e:
            logger.error(f"Error analyzing schema relationships: {e}")
            return f"Error analyzing schema relationships: {str(e)}"

    async def _get_cross_schema_relationships(
        self, schemas: List[str]
    ) -> List[Dict[str, Any]]:
        """Get foreign key relationships that cross schema boundaries."""
        if not schemas:
            return []

        # MySQL stores foreign key information in information_schema
        query = """
            SELECT DISTINCT
                tc.CONSTRAINT_SCHEMA as from_schema,
                tc.TABLE_NAME as from_table,
                GROUP_CONCAT(kcu.COLUMN_NAME ORDER BY kcu.ORDINAL_POSITION) as from_columns,
                kcu.REFERENCED_TABLE_SCHEMA as to_schema,
                kcu.REFERENCED_TABLE_NAME as to_table,
                GROUP_CONCAT(kcu.REFERENCED_COLUMN_NAME ORDER BY kcu.ORDINAL_POSITION) as to_columns,
                tc.CONSTRAINT_NAME
            FROM information_schema.TABLE_CONSTRAINTS tc
            JOIN information_schema.KEY_COLUMN_USAGE kcu
                ON tc.CONSTRAINT_NAME = kcu.CONSTRAINT_NAME
                AND tc.TABLE_SCHEMA = kcu.TABLE_SCHEMA
            WHERE tc.CONSTRAINT_TYPE = 'FOREIGN KEY'
                AND tc.CONSTRAINT_SCHEMA IN ({})
                AND kcu.REFERENCED_TABLE_SCHEMA IS NOT NULL
                AND tc.CONSTRAINT_SCHEMA != kcu.REFERENCED_TABLE_SCHEMA
            GROUP BY tc.CONSTRAINT_SCHEMA, tc.TABLE_NAME, kcu.REFERENCED_TABLE_SCHEMA,
                     kcu.REFERENCED_TABLE_NAME, tc.CONSTRAINT_NAME
            ORDER BY tc.CONSTRAINT_SCHEMA, tc.TABLE_NAME
        """.format(",".join([f"'{schema}'" for schema in schemas]))

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
                        "constraint_name": row_dict["CONSTRAINT_NAME"],
                    }
                    relationships.append(relationship)
        except Exception as e:
            logger.warning(f"Could not get cross-schema relationships: {e}")

        return relationships

    async def _analyze_schema_connectivity(
        self, schemas: List[str], relationships: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze connectivity patterns between schemas."""
        connectivity = {
            "schema_connections": {},
            "isolated_schemas": [],
            "hub_schemas": [],
            "dependency_chains": [],
        }

        # Count connections per schema
        schema_connections = {}
        for schema in schemas:
            schema_connections[schema] = {"outgoing": 0, "incoming": 0, "total": 0}

        for rel in relationships:
            from_schema = rel["from_schema"]
            to_schema = rel["to_schema"]

            if from_schema in schema_connections:
                schema_connections[from_schema]["outgoing"] += 1
                schema_connections[from_schema]["total"] += 1

            if to_schema in schema_connections:
                schema_connections[to_schema]["incoming"] += 1
                schema_connections[to_schema]["total"] += 1

        connectivity["schema_connections"] = schema_connections

        # Find isolated schemas (no cross-schema relationships)
        connectivity["isolated_schemas"] = [
            schema for schema, conn in schema_connections.items() if conn["total"] == 0
        ]

        # Find hub schemas (highly connected)
        hub_threshold = max(1, len(relationships) // len(schemas)) if schemas else 1
        connectivity["hub_schemas"] = [
            {"schema": schema, "connections": conn["total"]}
            for schema, conn in schema_connections.items()
            if conn["total"] >= hub_threshold
        ]
        connectivity["hub_schemas"].sort(key=lambda x: x["connections"], reverse=True)

        return connectivity

    def _format_schema_analysis(
        self,
        schemas: List[str],
        relationships: List[Dict[str, Any]],
        connectivity: Dict[str, Any],
    ) -> str:
        """Format schema analysis as agent-readable text."""
        output = []

        output.append("SCHEMA RELATIONSHIP ANALYSIS")
        output.append(f"Analyzed Schemas: {len(schemas)}")
        output.append(f"Cross-Schema Relationships: {len(relationships)}")
        output.append("")

        # Schema connectivity summary
        if connectivity["schema_connections"]:
            output.append("Schema Connectivity:")
            for schema, conn in connectivity["schema_connections"].items():
                if conn["total"] > 0:
                    output.append(
                        f"  - {schema}: {conn['total']} connections "
                        f"({conn['outgoing']} outgoing, {conn['incoming']} incoming)"
                    )
            output.append("")

        # Cross-schema relationships details
        if relationships:
            output.append("Cross-Schema Foreign Key Relationships:")
            for rel in relationships[:10]:  # Limit to top 10
                from_cols = ", ".join(rel["from_columns"])
                to_cols = ", ".join(rel["to_columns"])
                output.append(
                    f"  - {rel['from_schema']}.{rel['from_table']}({from_cols}) -> "
                    f"{rel['to_schema']}.{rel['to_table']}({to_cols})"
                )
            if len(relationships) > 10:
                output.append(f"  ... and {len(relationships) - 10} more relationships")
            output.append("")

        # Hub schemas
        if connectivity["hub_schemas"]:
            output.append("Most Connected Schemas:")
            for hub in connectivity["hub_schemas"][:5]:
                output.append(f"  - {hub['schema']}: {hub['connections']} connections")
            output.append("")

        # Isolated schemas
        if connectivity["isolated_schemas"]:
            output.append("Isolated Schemas (No Cross-Schema Relationships):")
            for schema in connectivity["isolated_schemas"]:
                output.append(f"  - {schema}")
            output.append("")

        # Insights
        output.append("Schema Architecture Insights:")
        total_schemas = len(schemas)
        connected_schemas = total_schemas - len(connectivity["isolated_schemas"])

        if len(connectivity["isolated_schemas"]) > 0:
            isolation_pct = (
                len(connectivity["isolated_schemas"]) / total_schemas
            ) * 100
            output.append(f"  - {isolation_pct:.1f}% of schemas are isolated")

        if connectivity["hub_schemas"]:
            hub_schema = connectivity["hub_schemas"][0]["schema"]
            hub_connections = connectivity["hub_schemas"][0]["connections"]
            output.append(
                f"  - '{hub_schema}' is the most connected schema ({hub_connections} connections)"
            )

        if len(relationships) == 0:
            output.append(
                "  - No cross-schema relationships found - schemas are independent"
            )
        elif connected_schemas == total_schemas:
            output.append(
                "  - All schemas are interconnected through foreign key relationships"
            )
        else:
            output.append(
                f"  - {connected_schemas}/{total_schemas} schemas are connected"
            )

        return "\n".join(output)
