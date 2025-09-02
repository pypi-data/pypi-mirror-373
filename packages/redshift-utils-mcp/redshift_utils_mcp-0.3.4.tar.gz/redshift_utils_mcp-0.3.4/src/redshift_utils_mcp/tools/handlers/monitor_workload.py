"""
MCP Tool Handler for Monitoring Redshift Workload Patterns.
"""

import asyncio
from typing import Dict, Any, List, Optional, Tuple, Union
from typing_extensions import TypedDict
from botocore.exceptions import ClientError
from mcp.server.fastmcp import Context
from ...server import mcp

from ...utils.data_api import (
    execute_sql,
    get_data_api_config,
    DataApiConfig,
    DataApiError,
    SqlExecutionError,
)
from ...utils.sql_loader import load_sql, SqlScriptNotFoundError


class ResourceTrends(TypedDict):
    cpu_peak_pct: Optional[float]
    spill_peak_mb: Optional[float]
    daily_query_counts: Dict[str, int]


class WLMPerformance(TypedDict):
    avg_queue_time_secs: Optional[float]
    concurrency_apex_current: Optional[int]
    concurrency_apex_historical: Optional[int]


class TopQuerySummary(TypedDict):
    query_id: int
    query_text_snippet: str
    total_execution_time_secs: float
    avg_execution_time_secs: float
    run_count: int
    total_cpu_secs: float
    total_spill_mb: float


class WorkloadCharacteristics(TypedDict):
    avg_queueing_queries: Optional[float]
    pct_disk_based_queries: Optional[float]
    slow_copy_summary: Optional[str]


class MonitorWorkloadResult(TypedDict):
    time_window_days: int
    resource_trends: ResourceTrends
    wlm_performance: WLMPerformance
    top_consuming_queries: List[TopQuerySummary]
    workload_characteristics: WorkloadCharacteristics
    potential_bottlenecks: List[str]
    errors: Optional[List[Dict[str, str]]]


@mcp.tool()
async def handle_monitor_workload(
    ctx: Context, time_window_days: int = 2, top_n_queries: int = 10
) -> Dict[str, Union[List[Dict[str, Any]], Exception]]:
    """Analyzes cluster workload patterns over a specified time window.

    Executes various SQL scripts concurrently to gather data on resource usage,
    WLM performance, top queries, queuing, COPY performance, and disk-based
    queries. Returns a dictionary containing the raw results (or Exceptions)
    keyed by the script name.

    Args:
        ctx: The MCP context object.
        time_window_days: Lookback period in days for the workload analysis.
                          Defaults to 2.
        top_n_queries: Number of top queries (by total execution time) to
                       consider for the 'top_queries.sql' script. Defaults to 10.

    Returns:
        A dictionary where keys are script names (e.g., 'workload/top_queries.sql')
        and values are either a list of result rows (as dictionaries) or the
        Exception object if that script failed.

    Raises:
        DataApiError: If a critical error occurs during configuration loading.
                      (Note: Individual script errors are returned in the result dict).
    """
    await ctx.info(
        f"Starting workload monitoring data collection (Window: {time_window_days} days, Top N: {top_n_queries})..."
    )

    scripts: List[str] = [
        "workload/queue_resources_hourly.sql",
        "workload/wlm_apex.sql",
        "workload/wlm_apex_hourly.sql",
        "workload/wlm_trend_daily.sql",
        "workload/wlm_trend_hourly.sql",
        "workload/top_queries.sql",
        "workload/queuing_summary.sql",
        "workload/copy_performance.sql",
        "workload/disk_based_query_count.sql",
        "workload/query_type_hourly_summary.sql",
    ]

    raw_results_dict: Dict[str, Union[List[Dict[str, Any]], Exception]] = {}
    tasks: List[asyncio.Task] = []

    async def run_script(script_name: str) -> None:
        """Loads and executes a single SQL script for workload monitoring."""
        nonlocal raw_results_dict
        await ctx.debug(f"Executing workload script: {script_name}")
        try:
            sql: str = load_sql(script_name)
            params: List[Tuple[str, Any]] = []
            if script_name in [
                "workload/queue_resources_hourly.sql",
                "workload/wlm_apex.sql",
                "workload/wlm_apex_hourly.sql",
                "workload/wlm_trend_daily.sql",
                "workload/wlm_trend_hourly.sql",
                "workload/queuing_summary.sql",
                "workload/copy_performance.sql",
                "workload/disk_based_query_count.sql",
            ]:
                params.append(("time_window_days", time_window_days))

            if script_name == "workload/top_queries.sql":
                params.append(("top_n_queries", top_n_queries))
                params.append(("time_window_days", time_window_days))

            config: DataApiConfig = get_data_api_config()
            result: Dict[str, Any] = await execute_sql(
                config=config, sql=sql, params=params if params else None
            )

            if result.get("error"):
                await ctx.warning(
                    f"Script {script_name} failed with error: {result['error']}"
                )

                raw_results_dict[script_name] = {"error": result["error"]}
            else:

                raw_results_dict[script_name] = result.get("rows", [])
        except SqlScriptNotFoundError as e:
            await ctx.error(
                f"SQL script not found for workload monitor: {script_name}",
                exc_info=True,
            )
            raw_results_dict[script_name] = e
        except (DataApiError, SqlExecutionError, ClientError, Exception) as e:
            await ctx.error(
                f"Error executing workload monitor script {script_name}: {e}",
                exc_info=True,
            )
            raw_results_dict[script_name] = e

    await ctx.debug(f"Executing {len(scripts)} workload scripts...")
    tasks = [asyncio.create_task(run_script(script)) for script in scripts]
    await asyncio.gather(*tasks)

    total_steps = len(scripts)
    await ctx.report_progress(total_steps, total_steps)

    await ctx.info("Workload monitoring data collection completed.")
    return raw_results_dict
