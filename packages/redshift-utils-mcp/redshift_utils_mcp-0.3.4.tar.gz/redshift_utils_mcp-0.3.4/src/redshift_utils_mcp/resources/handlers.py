# src/redshift_utils_mcp/resources/handlers.py
import logging
from typing import Any, Dict, List, Tuple  # Keep basic types

# Import Context for handlers

# Utility imports
from ..utils import data_api, sql_loader
from ..utils.data_api import DataApiConfig  # Keep specific exceptions
from ..utils.sql_loader import SqlScriptNotFoundError  # Keep specific exceptions

from ..server import mcp

logger = logging.getLogger(__name__)


@mcp.resource("/scripts/{script_path}")
async def handle_get_script_content(script_path: str) -> Tuple[bytes, str]:
    """Handles reading content for script:// URIs.

    This function is registered via @mcp.resource("script://{script_path:path}")
    in the server setup. It loads the content of the specified SQL script
    relative to the sql_scripts package directory.

    Args:
        script_path: The relative path (including subdirectories) of the script
                     within the sql_scripts package (e.g., 'health/disk_usage.sql').

    Returns:
        A tuple containing the script content as bytes and the MIME type ('text/plain').

    Raises:
        SqlScriptNotFoundError: If the specified script cannot be found.
        Exception: For any other unexpected errors during loading.
    """
    logger.info(f"Handling get_script_content for: {script_path}")
    try:
        content_str: str = sql_loader.load_sql(script_path)
        content_bytes: bytes = content_str.encode("utf-8")
        mime_type = "text/plain"

        return content_bytes, mime_type
    except SqlScriptNotFoundError:
        logger.error(f"Script not found: {script_path}")
        raise
    except Exception as e:
        logger.exception(f"Error loading script {script_path}: {e}")
        raise


# --- New Resource Handlers using Decorators ---


@mcp.resource("redshift://schemas")
async def get_schemas() -> List[str]:
    """
    Handles reading the list of user-defined schemas.
    Returns a list of schema names.
    """
    config: DataApiConfig = data_api.get_data_api_config()
    try:
        sql: str = sql_loader.load_sql("resources/list_schemas.sql")
    except SqlScriptNotFoundError as e:
        logger.exception("Failed to load list_schemas.sql script.")
        raise e
    results: List[Dict[str, Any]] = await data_api.execute_sql(config, sql)
    schema_names: List[str] = [
        row["schema_name"]
        for row in results
        if isinstance(row, dict) and "schema_name" in row
    ]
    return schema_names


@mcp.resource("redshift://wlm/configuration")
async def get_wlm_config() -> List[Dict[str, Any]]:
    """
    Handles reading the WLM configuration.
    Returns the WLM config as a list of dictionaries.
    """
    config: DataApiConfig = data_api.get_data_api_config()
    try:
        sql: str = sql_loader.load_sql("resources/get_wlm_config.sql")
    except SqlScriptNotFoundError as e:
        logger.exception("Failed to load get_wlm_config.sql script.")
        raise e
    results: List[Dict[str, Any]] = await data_api.execute_sql(config, sql)
    return results


@mcp.resource("redshift://schema/{schema_name}/tables")
async def list_tables_in_schema(schema_name: str) -> List[str]:
    """
    Handles reading the list of tables for a specific schema.
    Matches the URI template redshift://schema/{schema_name}/tables.
    Returns a list of table names.
    """
    config: DataApiConfig = data_api.get_data_api_config()
    try:
        sql: str = sql_loader.load_sql("resources/list_tables.sql")
    except SqlScriptNotFoundError as e:
        logger.exception(
            f"Failed to load list_tables.sql script for schema {schema_name}."
        )
        raise e
    params: List[Tuple[str, Any]] = [("schema_param", schema_name)]
    results: List[Dict[str, Any]] = await data_api.execute_sql(
        config, sql, params=params
    )
    table_names: List[str] = [
        row["table_name"]
        for row in results
        if isinstance(row, dict) and "table_name" in row
    ]
    return table_names
