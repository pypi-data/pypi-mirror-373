"""Handler for diagnosing lock contention."""

from typing import Dict, Any, List, Optional
from mcp.server.fastmcp import Context
from botocore.exceptions import ClientError

from ...utils.data_api import (
    DataApiConfig,
    get_data_api_config,
    execute_sql,
    SqlExecutionError,
    DataApiError,
)
from ...utils.sql_loader import load_sql, SqlScriptNotFoundError
from ...server import mcp


@mcp.tool()
async def handle_diagnose_locks(
    ctx: Context,
    target_pid: Optional[int] = None,
    target_table_name: Optional[str] = None,
    min_wait_seconds: int = 5,
) -> List[Dict[str, Any]]:
    """Identifies active lock contention in the cluster.

    Fetches all current lock information and then filters it based on the
    optional target PID, target table name, and minimum wait time.
    Formats the results into a list of contention details and a summary.

    Args:
        ctx: The MCP context object.
        target_pid: Optional: Filter results to show locks held by or waited
                    for by this specific process ID (PID).
        target_table_name: Optional: Filter results for locks specifically on
                           this table name (schema qualification recommended
                           if ambiguous).
        min_wait_seconds: Minimum seconds a lock must be in a waiting state
                          to be included. Defaults to 5.

    Returns:
        A list of dictionaries, where each dictionary represents a row
        from the lock contention query result.

    Raises:
        DataApiError: If fetching the initial lock information fails.
    """
    ctx.info("Starting lock diagnosis...")
    ctx.debug(
        f"Lock diagnosis filters - PID: {target_pid}, Table: {target_table_name}, MinWait: {min_wait_seconds}s"
    )

    lock_script: str = "locks/blocking_pids.sql"
    all_locks: List[Dict[str, Any]] = []

    try:
        sql: str = load_sql(lock_script)
        config: DataApiConfig = get_data_api_config()
        all_locks: List[Dict[str, Any]] = await execute_sql(config=config, sql=sql)
        ctx.debug(f"Retrieved {len(all_locks)} raw lock entries.")

    except (
        SqlScriptNotFoundError,
        DataApiError,
        SqlExecutionError,
        ClientError,
        Exception,
    ) as e:
        ctx.error(f"Failed to retrieve lock information: {e}", exc_info=True)
        raise DataApiError(f"Failed to retrieve lock information: {e}")

    ctx.info("Lock diagnosis completed.")
    return all_locks
