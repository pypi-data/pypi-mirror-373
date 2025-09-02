"""Handler for checking cluster health."""

import asyncio
from typing import Dict, Any, List, Optional, Tuple, Union
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
async def handle_check_cluster_health(
    ctx: Context, level: str = "basic", time_window_days: int = 1
) -> Dict[str, Union[List[Dict[str, Any]], Exception]]:
    """Performs a health assessment of the Redshift cluster.

    Executes a series of diagnostic SQL scripts concurrently based on the
    specified level ('basic' or 'full'). Aggregates raw results or errors
    from each script into a dictionary.

    Args:
        ctx: The MCP context object.
        level: Level of detail: 'basic' for operational status, 'full' for
               comprehensive table design/maintenance checks. Defaults to 'basic'.
        time_window_days: Lookback period in days for time-sensitive checks
                          (e.g., queue waits, commit waits). Defaults to 1.

    Returns:
        A dictionary where keys are script names and values are either the raw
        list of dictionary results from the SQL query or an Exception object
        if that specific script failed.

    Raises:
        DataApiError: If a critical error occurs during script execution that
                      prevents gathering results (e.g., config error). Individual
                      script errors are captured within the returned dictionary.
    """
    ctx.info(
        f"Starting cluster health check (level: {level}, window: {time_window_days} days)..."
    )

    basic_scripts: List[str] = [
        "health/disk_usage.sql",
        "health/queued_vs_total_queries.sql",
        "health/current_queries_status.sql",
        "locks/running_transaction_locks.sql",
        "workload/queuing_summary.sql" "workload/wlm_trend_hourly.sql",
    ]
    full_scripts_additional: List[str] = [
        "health/no_sort_key_count.sql",
        "health/dist_skew_count.sql",
        "health/top_alerts.sql",
    ]

    scripts_to_run: List[str] = basic_scripts
    if level == "full":
        scripts_to_run.extend(full_scripts_additional)

    raw_results_dict: Dict[str, Union[List[Dict[str, Any]], Exception]] = {}
    tasks: List[asyncio.Task] = []

    async def run_script(script_name: str) -> None:
        """Loads and executes a single SQL script, storing results or errors."""
        nonlocal raw_results_dict
        ctx.debug(f"Executing health script: {script_name}")
        try:
            sql: str = load_sql(script_name)
            params: Optional[List[Tuple[str, str]]] = None

            if script_name in [
                "health/top_alerts.sql",
                "health/queued_vs_total_queries.sql",
                "workload/queuing_summary.sql",
            ]:
                params = [("time_window_days", str(time_window_days))]

            config: DataApiConfig = get_data_api_config()
            result: List[Dict[str, Any]] = await execute_sql(
                config=config, sql=sql, params=params
            )
            raw_results_dict[script_name] = result
        except SqlScriptNotFoundError as e:
            ctx.error(
                f"SQL script not found for health check: {script_name}", exc_info=True
            )
            raw_results_dict[script_name] = e
        except (DataApiError, SqlExecutionError, ClientError, Exception) as e:
            ctx.error(
                f"Error executing health script {script_name}: {e}", exc_info=False
            )
            raw_results_dict[script_name] = e

    ctx.debug(f"Executing {len(scripts_to_run)} health check scripts...")

    tasks = [asyncio.create_task(run_script(script)) for script in scripts_to_run]

    await asyncio.gather(*tasks)

    total_steps = len(scripts_to_run)
    await ctx.report_progress(total_steps, total_steps)

    ctx.info("Cluster health check data gathering completed.")
    return raw_results_dict
