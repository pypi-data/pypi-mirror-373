"""Handler for diagnosing query performance."""

import asyncio
from typing import Dict, Any, List, Optional, Tuple, Union, cast

from botocore.exceptions import ClientError
from mcp.server.fastmcp import Context

from ...server import mcp
from ...utils.data_api import (
    DataApiConfig,
    get_data_api_config,
    execute_sql,
    SqlExecutionError,
    DataApiError,
)
from .common import QueryNotFound
from ...utils.sql_loader import load_sql, SqlScriptNotFoundError


@mcp.tool()
async def handle_diagnose_query_performance(
    ctx: Context, query_id: int, compare_historical: bool = True
) -> Dict[str, Union[List[Dict[str, Any]], Exception]]:
    """Analyzes a specific query's execution performance.

    Fetches query text, execution plan, metrics, alerts, compilation info,
    skew details, and optionally historical run data. Uses a formatting
    utility to synthesize this into a structured report with potential issues
    and recommendations.

    Args:
        ctx: The MCP context object.
        query_id: The numeric ID of the Redshift query to analyze.
        compare_historical: Fetch performance data for previous runs of the
                           same query text. Defaults to True.

    Returns:
        A dictionary conforming to DiagnoseQueryPerformanceResult structure:
        - On success: Contains detailed performance breakdown, issues, recommendations.
        - On query not found: Raises QueryNotFound exception.
        - On other errors: Raises DataApiError or similar for FastMCP to handle.

    Raises:
        DataApiError: If a critical error occurs during script execution or parsing.
        QueryNotFound: If the specified query_id cannot be found in key tables.
    """
    await ctx.info(
        f"Starting query performance diagnosis for query ID: {query_id} (Historical: {compare_historical})..."
    )

    base_scripts: List[str] = [
        "query_perf/query_text.sql",
        "query_perf/explain_plan.sql",
        "query_perf/segment_metrics.sql",
        "query_perf/overall_metrics.sql",
        "query_perf/query_alerts.sql",
        "query_perf/compilation_time.sql",
        "query_perf/slice_skew.sql",
    ]
    historical_script: str = "query_perf/historical_runs.sql"

    scripts_to_run: List[str] = list(base_scripts)
    if compare_historical:
        scripts_to_run.append(historical_script)

    raw_results_dict: Dict[str, Union[List[Dict[str, Any]], Exception]] = {}
    tasks: List[asyncio.Task] = []

    async def run_script(script_name: str) -> None:
        """Loads and executes a single SQL script for query diagnosis."""
        nonlocal raw_results_dict
        await ctx.debug(f"Executing performance script: {script_name}")
        try:
            sql: str = load_sql(script_name)

            params: List[Tuple[str, str]] = [("query_id", str(query_id))]

            if script_name == historical_script:
                params.append(("historical_limit", str(10)))

            config: DataApiConfig = get_data_api_config()
            result: List[Dict[str, Any]] = await execute_sql(
                config=config, sql=sql, params=params
            )

            if script_name == "query_perf/query_text.sql" and not result:

                raise QueryNotFound(
                    f"Query ID {query_id} not found or no performance data available."
                )

            raw_results_dict[script_name] = result
        except QueryNotFound:

            raise
        except SqlScriptNotFoundError:
            await ctx.error(
                f"SQL script not found for query perf: {script_name}", exc_info=True
            )

            raise
        except (
            DataApiError,
            SqlExecutionError,
            ClientError,
        ) as e:
            await ctx.error(
                f"Error executing performance script {script_name}: {e}", exc_info=False
            )

            raise

    await ctx.debug(f"Executing {len(scripts_to_run)} performance scripts...")

    tasks = [asyncio.create_task(run_script(script)) for script in scripts_to_run]
    results: List[Union[None, Exception]] = await asyncio.gather(
        *tasks, return_exceptions=True
    )

    total_steps = len(scripts_to_run)
    await ctx.report_progress(total_steps, total_steps)

    other_errors: List[Exception] = [
        res for res in results if isinstance(res, Exception)
    ]

    query_not_found_error: Optional[QueryNotFound] = None
    for res in results:
        if isinstance(res, QueryNotFound):
            query_not_found_error = res
            break

    if query_not_found_error:

        await ctx.warning(str(query_not_found_error))

        raise query_not_found_error

    if other_errors:
        await ctx.error(
            f"Errors encountered during query performance diagnosis: {other_errors}",
            exc_info=False,
        )

        raise DataApiError(
            f"Errors during query diagnosis: {other_errors[0]}"
        ) from other_errors[0]

    await ctx.debug(
        f"Skipping parsing for query ID: {query_id}. Returning raw results."
    )

    await ctx.info(
        f"Query performance diagnosis for query ID {query_id} completed (raw data)."
    )

    return cast(Dict[str, Union[List[Dict[str, Any]], Exception]], raw_results_dict)
