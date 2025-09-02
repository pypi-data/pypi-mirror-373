"""
Redshift Utils MCP Server Setup.

This module initializes the FastMCP server instance, registers all tool,
resource, and prompt handlers from their respective modules. It also defines
the server lifespan context manager (`server_lifespan`) which validates
the necessary AWS Redshift Data API configuration during startup.

The `mcp` instance created here is imported and run by the command-line
interface defined in `__main__.py`.
"""

import logging
import sys
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastmcp import FastMCP

from .utils.data_api import get_data_api_config, DataApiConfigError


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    stream=sys.stderr,
)
logging.getLogger("boto3").setLevel(logging.WARNING)
logging.getLogger("botocore").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def server_lifespan(mcp: "FastMCP") -> AsyncIterator[None]:
    """Asynchronous context manager for server startup and shutdown logic.

    This lifespan function is executed by FastMCP during server startup.
    It validates the required Redshift Data API configuration by attempting
    to retrieve it from environment variables. If validation fails, it logs
    an error and raises DataApiConfigError to prevent the server from starting.

    Args:
        mcp: The FastMCP server instance. Although not used directly in this
             lifespan function, it's provided by the FastMCP framework.
    """
    logger.info("Validating Redshift Data API configuration...")
    try:
        get_data_api_config()
        logger.info("Configuration validated successfully.")
    except DataApiConfigError as e:
        logger.error(f"Server startup failed: {e}")
        raise
    yield
    logger.info("Redshift Utils MCP Server shutting down.")


mcp: FastMCP = FastMCP(
    name="Redshift Utils MCP Server",
    lifespan=server_lifespan,
)


from .tools.handlers import (  # noqa: E402
    check_cluster_health,
    diagnose_locks,
    diagnose_query_performance,
    execute_ad_hoc_query,
    get_table_definition,
    inspect_table,
    monitor_workload,
)


from .resources import handlers as resource_handlers  # noqa: E402


from .prompts import handlers as prompt_handlers  # noqa: E402


_ = (
    check_cluster_health,
    diagnose_locks,
    diagnose_query_performance,
    execute_ad_hoc_query,
    get_table_definition,
    inspect_table,
    monitor_workload,
    resource_handlers,
    prompt_handlers,
)
