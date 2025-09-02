# src/redshift_utils_mcp/tools/handlers/__init__.py
"""Exports tool handlers."""
from .check_cluster_health import handle_check_cluster_health
from .diagnose_locks import handle_diagnose_locks
from .diagnose_query_performance import handle_diagnose_query_performance
from .execute_ad_hoc_query import handle_execute_ad_hoc_query
from .get_table_definition import handle_get_table_definition
from .inspect_table import handle_inspect_table
from .monitor_workload import handle_monitor_workload

__all__ = [
    "handle_check_cluster_health",
    "handle_diagnose_locks",
    "handle_diagnose_query_performance",
    "handle_execute_ad_hoc_query",
    "handle_get_table_definition",
    "handle_inspect_table",
    "handle_monitor_workload",
]
