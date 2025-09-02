"""Handler for retrieving table DDL."""

from typing import Dict, Any, List, Optional
from mcp.server.fastmcp import Context
from botocore.exceptions import ClientError

from .common import TableNotFound
from ...utils.data_api import (
    DataApiConfig,
    get_data_api_config,
    execute_sql,
    SqlExecutionError,
    DataApiError,
)
from ...utils.sql_loader import SqlScriptNotFoundError
from ...server import mcp


@mcp.tool()
async def handle_get_table_definition(
    ctx: Context, schema_name: str, table_name: str
) -> str:
    """Retrieves the DDL (Data Definition Language) statement for a specific table.

    Executes a SQL script designed to generate or retrieve the CREATE TABLE
    statement for the given table.

    Args:
        ctx: The MCP context object.
        schema_name: The schema name of the table.
        table_name: The name of the table.

    Returns:
        A dictionary conforming to GetTableDefinitionResult structure:
        - On success: {"status": "success", "ddl": "<CREATE TABLE statement>"}
        - On table not found or DDL retrieval error:
          {"status": "error", "error_message": "...", "error_type": "..."}

    Raises:
        TableNotFound: If the specified table is not found.
        DataApiError: If a critical, unexpected error occurs during execution.
    """
    ctx.info(f"Starting DDL retrieval for: {schema_name}.{table_name}...")

    sql: str = f"SHOW TABLE {schema_name}.{table_name}"
    ctx.debug(f"Executing command: {sql}")
    try:
        config: DataApiConfig = get_data_api_config()
        ddl_rows: List[Dict[str, Any]] = await execute_sql(
            config=config, sql=sql, params=None
        )

        if not ddl_rows:
            ctx.warning(
                f"Table '{schema_name}.{table_name}' not found or DDL could not be retrieved."
            )
            raise TableNotFound(
                f"Table '{schema_name}.{table_name}' not found or DDL could not be retrieved."
            )

        ctx.debug(f"Parsing DDL result for {schema_name}.{table_name}")
        first_row = ddl_rows[0]
        ddl_string: Optional[str] = list(first_row.values())[0] if first_row else None
        if not isinstance(ddl_string, str) or not ddl_string.strip().upper().startswith(
            "CREATE TABLE"
        ):
            ctx.error(
                f"DDL column missing or null in result for {schema_name}.{table_name}"
            )

            raise DataApiError(
                f"Could not extract DDL string for table '{schema_name}.{table_name}'. Query returned no DDL column."
            )

        ctx.info(f"DDL for {schema_name}.{table_name} retrieved successfully.")

        return ddl_string

    except TableNotFound as e:

        raise e
    except (
        SqlScriptNotFoundError,
        DataApiError,
        SqlExecutionError,
        ClientError,
    ) as e:
        ctx.error(
            f"SQL execution failed while retrieving DDL for {schema_name}.{table_name}: {e}",
            exc_info=True,
        )
        raise
    except Exception as e:
        ctx.error(f"Unexpected error getting DDL for {schema_name}.{table_name}: {e}")
        raise DataApiError(
            f"An unexpected server error occurred while retrieving DDL: {e}"
        )
