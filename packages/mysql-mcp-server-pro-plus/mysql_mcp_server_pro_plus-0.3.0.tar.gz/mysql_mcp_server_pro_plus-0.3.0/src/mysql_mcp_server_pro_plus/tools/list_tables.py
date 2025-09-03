from ..logger import logger


async def list_tables_tool(db_manager) -> str:
    """List all tables in the database.

    Args:
        db_manager: Database manager instance
    """
    try:
        logger.info("Listing database tables")

        if not db_manager:
            raise RuntimeError("Database manager not initialized")

        tables = await db_manager.get_tables()
        if tables:
            return "\n".join(tables)
        else:
            return "No tables found"

    except Exception as e:
        logger.error(f"Error listing tables: {e}")
        return f"Error: {str(e)}"
