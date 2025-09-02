"""Handler for inspecting table details."""

import asyncio
from typing import Dict, Any, List, Optional, Tuple, Union
from botocore.exceptions import ClientError
from mcp.server.fastmcp import Context

from ...server import mcp
from .common import TableNotFound
from ...utils.data_api import (
    DataApiConfig,
    get_data_api_config,
    execute_sql,
    SqlExecutionError,
    DataApiError,
)
from ...utils.sql_loader import load_sql, SqlScriptNotFoundError


@mcp.tool()
async def handle_inspect_table(
    ctx: Context, schema_name: str, table_name: str
) -> Dict[str, Union[List[Dict[str, Any]], str, Exception]]:
    """Retrieves detailed information about a specific Redshift table.

    Fetches table OID, then concurrently executes various inspection scripts
    covering design, storage, health, usage, and encoding.

    Args:
        ctx: The MCP context object.
        schema_name: The schema name of the table.
        table_name: The name of the table.

    Returns:
        A dictionary where keys are script names and values are either the raw
        list of dictionary results from the SQL query, the extracted DDL string,
        or an Exception object if that specific script failed.
        - On success: Dictionary containing raw results or Exception objects for each script.
        - On table not found: Raises TableNotFound exception.
        - On critical errors (e.g., OID lookup failure): Raises DataApiError or similar.

    Raises:
        DataApiError: If a critical error occurs during script execution.
        TableNotFound: If the specified table cannot be found via its OID.
    """
    await ctx.info(f"Starting table inspection for: {schema_name}.{table_name}...")

    oid_script: str = "table_inspect/get_oid.sql"
    detail_scripts: List[str] = [
        "table_inspect/table_info.sql",
        "table_inspect/table_inspector.sql",
        "table_inspect/table_top_queries.sql",
        "table_inspect/scan_frequency.sql",
        "table_inspect/vacuum_history.sql",
        "table_inspect/get_table_ddl.sql",
    ]

    raw_results_dict: Dict[str, Union[List[Dict[str, Any]], Exception]] = {}
    table_oid: Optional[int] = None

    await ctx.debug(f"Attempting to retrieve OID for table: {schema_name}.{table_name}")

    try:
        sql_oid: str = load_sql(oid_script)
        params_oid: List[Tuple[str, str]] = [
            ("schema_name", schema_name),
            ("table_name", table_name),
        ]
        config: DataApiConfig = get_data_api_config()
        oid_rows: List[Dict[str, Any]] = await execute_sql(
            config=config, sql=sql_oid, params=params_oid
        )

        if not oid_rows:
            raise TableNotFound(f"Table '{schema_name}.{table_name}' not found.")

        table_oid_any = oid_rows[0].get("oid")
        if table_oid_any is None:
            raise TableNotFound(
                f"Could not retrieve OID for table '{schema_name}.{table_name}'. OID column missing or null."
            )

        try:
            table_oid = int(table_oid_any)
        except (ValueError, TypeError):
            raise TableNotFound(
                f"Retrieved invalid OID '{table_oid_any}' for table '{schema_name}.{table_name}'."
            )

        raw_results_dict[oid_script] = oid_rows
        await ctx.debug(
            f"Retrieved OID {table_oid} for table {schema_name}.{table_name}"
        )

    except TableNotFound as e:
        await ctx.warning(str(e))
        raise e
    except (
        SqlScriptNotFoundError,
        DataApiError,
        SqlExecutionError,
        ClientError,
        Exception,
    ) as e:
        await ctx.error(f"Error getting OID for table {schema_name}.{table_name}: {e}")

        raise DataApiError(
            f"Failed to retrieve table OID for {schema_name}.{table_name}: {e}"
        )

    tasks: List[asyncio.Task] = []

    async def run_detail_script(script_name: str) -> None:
        """Loads and executes a single detail script for table inspection."""
        nonlocal raw_results_dict
        await ctx.debug(
            f"Executing inspection script: {script_name} for OID {table_oid}"
        )
        try:
            sql: str
            params: Optional[List[Tuple[str, str]]] = None
            is_ddl_script = script_name == "table_inspect/get_table_ddl.sql"

            if is_ddl_script:
                safe_schema = (
                    f'"{schema_name}"' if '"' not in schema_name else schema_name
                )
                safe_table = f'"{table_name}"' if '"' not in table_name else table_name
                sql = f"SHOW TABLE {safe_schema}.{safe_table}"
                params = None
            else:
                sql = load_sql(script_name)
                if script_name in [
                    "table_inspect/table_info.sql",
                    "table_inspect/table_inspector.sql",
                ]:
                    params = [
                        ("schema_name", schema_name),
                        ("table_name", table_name),
                    ]
                elif script_name in [
                    "table_inspect/table_top_queries.sql",
                    "table_inspect/scan_frequency.sql",
                    "table_inspect/vacuum_history.sql",
                ]:
                    params = [
                        ("table_id", str(table_oid)),
                    ]
                elif script_name in [
                    "table_inspect/missing_stats_count.sql",
                    "table_inspect/stale_stats_count.sql",
                    "table_inspect/needs_vacuum_count.sql",
                ]:
                    params = None
                else:
                    await ctx.warning(
                        f"Unknown script '{script_name}' encountered in run_detail_script. Attempting without parameters."
                    )
                    params = None

            config: DataApiConfig = get_data_api_config()
            result: List[Dict[str, Any]] = await execute_sql(
                config=config, sql=sql, params=params if params else None
            )

            if is_ddl_script:
                extracted_ddl: Optional[str] = None
                if (
                    result
                    and isinstance(result, list)
                    and len(result) > 0
                    and isinstance(result[0], dict)
                ):
                    first_row = result[0]
                    if "ddl" in first_row and isinstance(first_row["ddl"], str):
                        extracted_ddl = first_row["ddl"]
                    elif "create table statement" in first_row and isinstance(
                        first_row["create table statement"], str
                    ):
                        extracted_ddl = first_row["create table statement"]
                    elif first_row:
                        first_value = next(iter(first_row.values()), None)
                        if isinstance(first_value, str):
                            extracted_ddl = first_value
                raw_results_dict[script_name] = extracted_ddl
                await ctx.debug(
                    f"Extracted DDL for {script_name}: {extracted_ddl[:100] if extracted_ddl else 'None'}..."
                )
            else:
                raw_results_dict[script_name] = result

        except SqlScriptNotFoundError as e:
            await ctx.error(f"SQL script not found for table inspect: {script_name}")
            raw_results_dict[script_name] = e
            raise e
        except (DataApiError, SqlExecutionError, ClientError, Exception) as e:
            await ctx.error(f"Error executing inspection script {script_name}: {e}")
            raw_results_dict[script_name] = e
            raise e

    await ctx.debug(
        f"Executing {len(detail_scripts)} detail scripts for table OID {table_oid}..."
    )
    tasks = [
        asyncio.create_task(run_detail_script(script)) for script in detail_scripts
    ]
    results_detail = await asyncio.gather(*tasks, return_exceptions=True)

    total_steps = 1 + len(detail_scripts)
    await ctx.report_progress(total_steps, total_steps)

    detail_errors = [res for res in results_detail if isinstance(res, Exception)]
    if detail_errors:
        await ctx.error(
            f"Errors encountered during table detail inspection: {detail_errors}"
        )
        raise DataApiError(
            f"Errors during table inspection: {detail_errors[0]}"
        ) from detail_errors[0]

    await ctx.info(
        f"Table inspection data gathering for {schema_name}.{table_name} completed."
    )
    await ctx.debug(f"Returning raw results dictionary for {schema_name}.{table_name}")
    return raw_results_dict
