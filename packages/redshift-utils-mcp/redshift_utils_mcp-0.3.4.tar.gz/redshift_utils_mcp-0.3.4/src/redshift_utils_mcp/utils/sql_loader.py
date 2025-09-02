import importlib.resources
import logging


logger = logging.getLogger(__name__)


class SqlScriptNotFoundError(Exception):
    """Custom exception raised when an SQL script cannot be found."""

    pass


def load_sql(script_name: str) -> str:
    """
    Loads SQL script content from the sql_scripts directory.

    Args:
        script_name: The relative path to the SQL script from the
                     'src/redshift_utils_mcp/sql_scripts' directory
                     (e.g., 'health/cpu_monitor.sql').

    Returns:
        The content of the SQL script as a string.

    Raises:
        SqlScriptNotFoundError: If the specified script cannot be found.
    """
    logger.debug(f"Attempting to load SQL script: {script_name}")
    try:

        script_path = importlib.resources.files(
            "redshift_utils_mcp.sql_scripts"
        ).joinpath(script_name)
        content = script_path.read_text(encoding="utf-8")
        logger.debug(f"Successfully loaded SQL script: {script_name}")
        return content
    except FileNotFoundError:
        logger.error(f"SQL script '{script_name}' not found.")
        raise SqlScriptNotFoundError(f"SQL script '{script_name}' not found")
    except Exception as e:

        logger.error(
            f"Unexpected error loading SQL script '{script_name}': {e}", exc_info=True
        )

        raise SqlScriptNotFoundError(
            f"Could not load SQL script '{script_name}' due to an unexpected error: {e}"
        ) from e
