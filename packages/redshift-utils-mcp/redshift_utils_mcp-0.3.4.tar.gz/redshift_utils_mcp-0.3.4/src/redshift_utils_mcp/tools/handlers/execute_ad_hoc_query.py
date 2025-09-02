"""Handler for executing ad-hoc SQL queries."""

from typing import Dict, Any, List

from mcp.server.fastmcp import Context
from botocore.exceptions import ClientError

from .common import (
    ExecuteAdHocQueryResult,
    ExecuteAdHocQuerySuccessResult,
)
from ...utils.data_api import (
    DataApiConfig,
    get_data_api_config,
    execute_sql,
    DataApiConfigError,
    SqlExecutionError,
    DataApiTimeoutError,
    DataApiError,
)
from ...server import mcp


@mcp.tool()
async def handle_execute_ad_hoc_query(
    ctx: Context, sql_query: str
) -> ExecuteAdHocQueryResult:
    """Executes an arbitrary SQL query provided by the user via Redshift Data API.

    Designed as an escape hatch for advanced users or queries not covered by
    specialized tools. Returns a structured dictionary indicating success
    (with results) or failure (with error details).

    Args:
        ctx: The MCP context object.
        sql_query: The exact SQL query string to execute.

    Returns:
        A dictionary conforming to ExecuteAdHocQueryResult structure:
        - On success: {"status": "success", "columns": [...], "rows": [...], "row_count": ...}
        - On error: {"status": "error", "error_message": "...", "error_type": "..."}
        (Note: Actual return might be handled by FastMCP error handling for raised exceptions)

    Raises:
        DataApiConfigError: If configuration is invalid.
        SqlExecutionError: If the SQL execution itself fails.
        DataApiTimeoutError: If the Data API call times out.
        DataApiError: For other Data API related errors or unexpected issues.
        ClientError: For AWS client-side errors.
    """
    ctx.info(f"Executing ad-hoc query: {sql_query[:100]}...")
    ctx.debug(f"Executing ad-hoc SQL: {sql_query}")
    try:

        config: DataApiConfig = get_data_api_config()
        result_data: List[Dict[str, Any]] = await execute_sql(
            config=config, sql=sql_query
        )

        columns: List[Dict[str, Any]] = []
        rows: List[Dict[str, Any]] = result_data
        row_count: int = len(rows)

        ctx.info(f"Ad-hoc query executed successfully. Rows returned: {row_count}")

        success_result: ExecuteAdHocQuerySuccessResult = {
            "status": "success",
            "columns": columns,
            "rows": rows,
            "row_count": row_count,
        }
        return success_result
    except DataApiConfigError as e:
        ctx.error(f"Data API configuration error for ad-hoc query: {e}", exc_info=True)
        raise
    except (
        SqlExecutionError,
        DataApiTimeoutError,
        DataApiError,
        ClientError,
    ) as e:

        ctx.error(f"SQL execution failed for ad-hoc query: {e}", exc_info=True)
        raise
    except Exception as e:
        ctx.error(f"Unexpected error executing ad-hoc query: {e}", exc_info=True)

        raise DataApiError(f"An unexpected server error occurred: {e}")
