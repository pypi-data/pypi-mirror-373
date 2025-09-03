from ..logger import logger


async def execute_sql_tool(query: str, db_manager, security_validator) -> str:
    """Execute an SQL query on the MySQL server.

    Args:
        query: The SQL query to execute
        db_manager: Database manager instance
        security_validator: Security validator instance
    """
    try:
        logger.info(f"Executing SQL query: {query[:100]}...")

        if not db_manager or not security_validator:
            raise RuntimeError("Server not properly initialized")

        # Validate and sanitize query
        validated_query = security_validator.validate_query(query)

        # Execute query
        result = await db_manager.execute_query(validated_query)

        if result.has_results:
            # Format results as CSV
            lines = [",".join(result.columns)]
            for row in result.rows:
                lines.append(",".join(str(cell) for cell in row))
            return "\n".join(lines)
        else:
            return f"Query executed successfully. Rows affected: {result.row_count}"

    except Exception as e:
        logger.error(f"SQL execution error: {e}")
        return f"Error: {str(e)}"
