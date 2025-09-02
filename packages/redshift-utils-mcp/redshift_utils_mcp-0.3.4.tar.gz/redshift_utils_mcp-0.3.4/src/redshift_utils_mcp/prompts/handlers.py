from ..server import mcp


@mcp.prompt()
async def run_health_check(level: str = "basic") -> str:
    """
    Guides the agent to perform a health check of the Redshift cluster.

    Args:
        level: Level of detail ('basic' or 'full'). Default: 'basic'.
    """
    # Return an instruction for the agent
    return f"Please call the 'handle_check_cluster_health' tool with the following arguments: level='{level}'"


@mcp.prompt()
async def analyze_slow_query(query_id: int) -> str:
    """
    Guides the agent to analyze the performance of a specific Redshift query.

    Args:
        query_id: The numeric ID of the query to analyze.
    """
    # Return an instruction for the agent
    return f"Please call the 'handle_diagnose_query_performance' tool with the following arguments: query_id={query_id}"


@mcp.prompt()
async def check_table_health(schema_name: str, table_name: str) -> str:
    """
    Guides the agent to assess the health, design, and maintenance status of a specific table.

    Args:
        schema_name: The schema name of the table.
        table_name: The name of the table.
    """
    # Return an instruction for the agent
    return f"Please call the 'handle_inspect_table' tool with the following arguments: schema_name='{schema_name}', table_name='{table_name}'"


@mcp.prompt()
async def find_blocking_locks() -> str:
    """
    Guides the agent to identify current lock contention and blocking sessions.
    """
    # Return an instruction for the agent
    return "Please call the 'handle_diagnose_locks' tool."
