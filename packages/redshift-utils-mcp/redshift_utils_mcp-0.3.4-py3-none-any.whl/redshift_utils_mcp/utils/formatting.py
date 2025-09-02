from typing import List, Dict, Any, Optional, Set, Union, cast
from typing_extensions import TypedDict


class HealthCheckItem(TypedDict, total=False):
    check_name: str
    status: str
    value: Any
    unit: Optional[str]
    threshold: Optional[Union[int, float]]
    details: str


class ParsedHealthCheckResult(TypedDict):
    overall_status: str
    checks: List[HealthCheckItem]
    recommendations: List[str]


class QueryPerformanceMetrics(TypedDict, total=False):

    duration_sec: Optional[float]
    queue_time_sec: Optional[float]
    cpu_time_sec: Optional[float]
    compile_time_sec: Optional[float]

    cpu_skew: Optional[float]
    io_skew: Optional[float]

    scan_row_count: Optional[int]
    join_row_count: Optional[int]
    return_row_count: Optional[int]

    scan_blocks_read: Optional[int]
    spill_size_mb: Optional[int]

    result_cache_hit: Optional[bool]
    query_priority: Optional[str]
    query_type: Optional[str]
    wlm_service_class_id: Optional[int]
    wlm_service_class_name: Optional[str]


class ParsedQueryPerformanceResult(TypedDict, total=False):
    query_id: int
    query_text: str
    overall_metrics: QueryPerformanceMetrics
    segment_metrics: List[Dict[str, Any]]
    slice_skew: List[Dict[str, Any]]
    explain_plan: List[Dict[str, Any]]
    historical_runs: List[Dict[str, Any]]
    potential_issues: List[Any]
    recommendations: List[str]


class TableBasicInfo(TypedDict, total=False):
    size_mb: Optional[float]
    rows: Optional[int]
    dist_style: Optional[str]
    dist_key: Optional[str]
    sort_keys: Optional[Union[str, List[str]]]


class TablePerformanceStats(TypedDict, total=False):
    scan_frequency: Optional[int]

    missing_stats_count: int
    stale_stats_count: int
    needs_vacuum: bool


class ParsedInspectTableResult(TypedDict, total=False):
    table_identifier: str
    basic_info: TableBasicInfo
    column_details: List[Dict[str, Any]]
    ddl: Optional[str]
    performance_stats: TablePerformanceStats
    potential_issues: List[Dict[str, Any]]
    vacuum_history: List[Dict[str, Any]]
    recommendations: List[str]


class WorkloadSummary(TypedDict, total=False):
    active_sessions: int
    queries_executing: int
    queries_queued: int
    avg_commit_wait_ms: Optional[float]
    disk_based_queries_recent: int


class WorkloadTrends(TypedDict, total=False):
    apex: List[Dict[str, Any]]
    hourly_trend: List[Dict[str, Any]]


class ParsedMonitorWorkloadResult(TypedDict, total=False):
    summary: WorkloadSummary
    wlm_state: List[Dict[str, Any]]
    queue_performance: List[Dict[str, Any]]
    top_active_queries: List[Dict[str, Any]]
    recent_copy_performance: List[Dict[str, Any]]
    workload_trends: WorkloadTrends
    potential_issues: List[str]
    recommendations: List[str]


def _get_first_value(
    data_list: Optional[List[Dict[str, Any]]], key: str, default: Any = None
) -> Any:
    """Safely get the value of a key from the first dictionary in a list.

    Args:
        data_list: A list potentially containing dictionaries, or None.
        key: The dictionary key to retrieve the value for.
        default: The value to return if the list is empty, None, not a list,
                 the first item is not a dict, or the key is not found.

    Returns:
        The value associated with the key in the first dictionary, or the default value.
    """
    if (
        data_list
        and isinstance(data_list, list)
        and len(data_list) > 0
        and isinstance(data_list[0], dict)
    ):
        return data_list[0].get(key, default)
    return default


def _get_list_value(
    data_dict: Optional[Dict[str, List[Dict[str, Any]]]],
    key: str,
    default: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """Safely get a list value from a dictionary, ensuring it's a list of dicts.

    Args:
        data_dict: A dictionary potentially containing lists, or None.
        key: The dictionary key whose value is expected to be a list.
        default: The default list to return if the key is not found, the value
                 is not a list, or the input dict is invalid. Defaults to an empty list.

    Returns:
        The list associated with the key, or the default list.
    """
    if default is None:
        default = []
    if not data_dict or not isinstance(data_dict, dict):
        return default

    value = data_dict.get(key)
    return value if isinstance(value, list) else default


def parse_health_check_results(
    raw_results_dict: Dict[str, Union[List[Dict[str, Any]], Exception]],
) -> ParsedHealthCheckResult:
    """Parses raw health check results from multiple scripts into the expected MCP tool output format.

    Accepts a dictionary where keys are script paths (e.g., 'health/cpu_monitor.sql')
    and values are either a list of result rows (dictionaries) or an Exception if
    the script execution failed.

    Generates recommendations based on specific check names and values exceeding
    thresholds or having non-standard details. The overall status is marked
    'Warning' if any check indicates a warning state.

    Args:
        raw_results_dict: A dictionary mapping script paths to their results (list of dicts)
                          or an Exception object.

    Returns:
        A dictionary containing the overall status ('OK' or 'Warning'), a list
        of parsed checks with their individual status and details, and a list
        of generated recommendations.
    """
    parsed_checks: List[HealthCheckItem] = []
    recommendations: List[str] = []
    errors_encountered: List[str] = []
    overall_warning: bool = False

    cpu_script_key = "health/cpu_monitor.sql"
    cpu_results_or_error = raw_results_dict.get(cpu_script_key)

    if isinstance(cpu_results_or_error, list):
        max_peak_cpu: float = 0.0
        peak_node: Optional[int] = None
        avg_cpu_sum: float = 0.0
        node_count: int = 0

        for node_data in cpu_results_or_error:
            if isinstance(node_data, dict):
                node_count += 1
                peak = node_data.get("peak_cpu_utilization_last_hour")
                avg = node_data.get("avg_cpu_utilization_last_hour")

                if isinstance(peak, (int, float)):
                    if peak > max_peak_cpu:
                        max_peak_cpu = float(peak)
                        peak_node = node_data.get("node")
                if isinstance(avg, (int, float)):
                    avg_cpu_sum += float(avg)

        cpu_threshold = 90.0
        cpu_status = "OK"
        cpu_details = (
            f"Highest peak CPU usage across nodes in the last hour: {max_peak_cpu:.2f}%"
        )
        if peak_node is not None:
            cpu_details += f" (on node {peak_node})"

        if max_peak_cpu > cpu_threshold:
            cpu_status = "Warning"
            overall_warning = True
            recommendations.append(
                f"Peak CPU Utilization reached {max_peak_cpu:.2f}% (node {peak_node}). Check running queries or consider scaling."
            )

        parsed_checks.append(
            HealthCheckItem(
                check_name="Peak CPU Utilization (Last Hour)",
                status=cpu_status,
                value=f"{max_peak_cpu:.2f}",
                unit="%",
                threshold=cpu_threshold,
                details=cpu_details,
            )
        )

    elif isinstance(cpu_results_or_error, Exception):
        errors_encountered.append(
            f"Failed to retrieve CPU utilization: {cpu_results_or_error}"
        )
        parsed_checks.append(
            HealthCheckItem(
                check_name="Peak CPU Utilization (Last Hour)",
                status="Error",
                details=f"Could not retrieve data: {cpu_results_or_error}",
            )
        )
        overall_warning = True

    disk_script_key = "health/disk_usage.sql"
    disk_results_or_error = raw_results_dict.get(disk_script_key)
    disk_threshold = 85.0

    if isinstance(disk_results_or_error, list):
        disk_usage_pct_str = _get_first_value(
            disk_results_or_error, "total_disk_usage_pct"
        )
        disk_usage_pct: Optional[float] = None
        try:
            if disk_usage_pct_str is not None:
                disk_usage_pct = float(disk_usage_pct_str)
        except (ValueError, TypeError):
            disk_usage_pct = None

        if disk_usage_pct is not None:
            disk_status = "OK"
            disk_details = f"Total cluster disk usage: {disk_usage_pct:.2f}%"
            if disk_usage_pct > disk_threshold:
                disk_status = "Warning"
                overall_warning = True
                recommendations.append(
                    f"Total Disk Usage is high ({disk_usage_pct:.2f}%). Consider vacuuming tables, archiving old data, or resizing the cluster."
                )
            parsed_checks.append(
                HealthCheckItem(
                    check_name="Total Disk Usage",
                    status=disk_status,
                    value=f"{disk_usage_pct:.2f}",
                    unit="%",
                    threshold=disk_threshold,
                    details=disk_details,
                )
            )
        else:
            errors_encountered.append(
                f"Unexpected data format for {disk_script_key}: {disk_results_or_error}"
            )
            parsed_checks.append(
                HealthCheckItem(
                    check_name="Total Disk Usage",
                    status="Error",
                    details="Could not parse disk usage percentage.",
                )
            )
            overall_warning = True
    elif isinstance(disk_results_or_error, Exception):
        errors_encountered.append(
            f"Failed to retrieve disk usage: {disk_results_or_error}"
        )
        parsed_checks.append(
            HealthCheckItem(
                check_name="Total Disk Usage",
                status="Error",
                details=f"Could not retrieve data: {disk_results_or_error}",
            )
        )
        overall_warning = True

    wlm_script_key = "workload/wlm_queue_state.sql"
    wlm_results_or_error = raw_results_dict.get(wlm_script_key)
    queue_count_threshold = 10
    queue_wait_threshold_sec = 300

    if isinstance(wlm_results_or_error, list):
        for queue_data in wlm_results_or_error:
            if isinstance(queue_data, dict):
                sc = queue_data.get("service_class")
                queued = queue_data.get("queued_count")
                executing = queue_data.get("executing_count")
                max_wait_sec = queue_data.get("max_queue_wait_seconds")

                if sc is None:
                    continue

                q_status = "OK"
                q_details = f"SC {sc}: Queued={queued}, Executing={executing}"
                if isinstance(queued, int) and queued > queue_count_threshold:
                    q_status = "Warning"
                    overall_warning = True
                    recommendations.append(
                        f"High queue count ({queued}) in Service Class {sc}. Check WLM config or long-running queries."
                    )
                    q_details += f" (Threshold: {queue_count_threshold})"

                parsed_checks.append(
                    HealthCheckItem(
                        check_name=f"WLM Queue Count (SC {sc})",
                        status=q_status,
                        value=queued,
                        unit="queries",
                        threshold=queue_count_threshold,
                        details=q_details,
                    )
                )

                w_status = "OK"
                w_details = (
                    f"SC {sc}: Max Wait={max_wait_sec:.2f}s"
                    if isinstance(max_wait_sec, (int, float))
                    else f"SC {sc}: Max Wait=N/A"
                )
                if (
                    isinstance(max_wait_sec, (int, float))
                    and max_wait_sec > queue_wait_threshold_sec
                ):
                    w_status = "Warning"
                    overall_warning = True
                    recommendations.append(
                        f"Long queue wait time ({max_wait_sec:.2f}s) in Service Class {sc}. Check WLM config or resource contention."
                    )
                    w_details += f" (Threshold: {queue_wait_threshold_sec}s)"

                parsed_checks.append(
                    HealthCheckItem(
                        check_name=f"WLM Max Queue Wait (SC {sc})",
                        status=w_status,
                        value=(
                            f"{max_wait_sec:.2f}"
                            if isinstance(max_wait_sec, (int, float))
                            else "N/A"
                        ),
                        unit="seconds",
                        threshold=queue_wait_threshold_sec,
                        details=w_details,
                    )
                )

    elif isinstance(wlm_results_or_error, Exception):
        errors_encountered.append(
            f"Failed to retrieve WLM queue state: {wlm_results_or_error}"
        )
        parsed_checks.append(
            HealthCheckItem(
                check_name="WLM Queue State",
                status="Error",
                details=f"Could not retrieve data: {wlm_results_or_error}",
            )
        )
        overall_warning = True

    other_check_results: List[Dict[str, Any]] = []
    for script_key, result_or_error in raw_results_dict.items():

        if script_key in [
            cpu_script_key,
            disk_script_key,
            wlm_script_key,
        ]:
            continue

        if isinstance(result_or_error, list):
            if len(result_or_error) == 1 and isinstance(result_or_error[0], dict):
                other_check_results.append(result_or_error[0])

        elif isinstance(result_or_error, Exception):
            errors_encountered.append(
                f"Error executing {script_key}: {result_or_error}"
            )
            check_name_from_key = (
                script_key.replace(".sql", "")
                .replace("health/", "")
                .replace("workload/", "")
                .replace("locks/", "")
                .replace("table_inspect/", "")
                .replace("_", " ")
                .title()
            )
            parsed_checks.append(
                HealthCheckItem(
                    check_name=f"{check_name_from_key} Check",
                    status="Error",
                    details=f"Could not retrieve data: {result_or_error}",
                )
            )
            overall_warning = True

    check: Dict[str, Any]
    for check in other_check_results:
        if not isinstance(check, dict):
            continue

        try:
            name: Optional[str] = check.get("check_name")
            value: Any = check.get("metric_value")
            threshold: Optional[Union[int, float]] = check.get("threshold")
            unit: Optional[str] = check.get("unit")
            details: str = check.get("recommendation", "N/A")

            if name is None:
                if "num_blocking_locks" in check:
                    name = "Blocking Locks"
                    value = check["num_blocking_locks"]
                    unit = "locks"
                    threshold = 0
                    details = (
                        f"{value} blocking lock(s) detected."
                        if isinstance(value, int) and value > 0
                        else "Normal"
                    )
                elif "missing_stats_count" in check:
                    name = "Missing Table Statistics"
                    value = check["missing_stats_count"]
                    unit = "tables"
                    threshold = 0
                    details = (
                        f"{value} table(s) missing statistics."
                        if isinstance(value, int) and value > 0
                        else "Normal"
                    )
                elif "dist_skew_count" in check:
                    name = "Distribution Skew"
                    value = check["dist_skew_count"]
                    unit = "tables"
                    threshold = 0
                    details = (
                        f"{value} table(s) have significant distribution skew (skew_rows > 4)."
                        if isinstance(value, int) and value > 0
                        else "Normal"
                    )
                elif "underrepped_blocks_count" in check:
                    name = "Under-replicated Blocks"
                    value = check["underrepped_blocks_count"]
                    unit = "blocks"
                    threshold = 0
                    details = (
                        f"{value} block(s) found with < 2 replicas."
                        if isinstance(value, int) and value > 0
                        else "Normal"
                    )
                elif "max_commit_wait_seconds" in check:
                    name = "Max Commit Wait Time"
                    value = check["max_commit_wait_seconds"]
                    unit = "seconds"
                    threshold = 60
                    details = (
                        f"Maximum commit queue wait time in the last {check.get('time_window_days', 'N/A')} days: {value}s."
                        if isinstance(value, (int, float))
                        else "N/A"
                    )
                elif "stale_stats_count" in check:
                    name = "Stale Statistics Count"
                    value = check["stale_stats_count"]
                    unit = "tables"
                    threshold = 0
                    details = (
                        f"{value} table(s) have stale statistics."
                        if isinstance(value, int) and value > 0
                        else "Normal"
                    )
                elif "needs_vacuum_count" in check:
                    name = "Tables Needing Vacuum"
                    value = check["needs_vacuum_count"]
                    unit = "tables"
                    threshold = 0
                    details = (
                        f"{value} table(s) may benefit from VACUUM (based on unsorted rows or deleted rows)."
                        if isinstance(value, int) and value > 0
                        else "Normal"
                    )
                else:
                    errors_encountered.append(
                        f"Could not determine check name or metric value for result: {check}"
                    )
                    continue

            if name is None or value is None:
                errors_encountered.append(f"Missing name or value for check: {check}")
                continue

            status: str = "OK"
            if (
                threshold is not None
                and isinstance(value, (int, float))
                and isinstance(threshold, (int, float))
                and value > threshold
            ):
                status = "Warning"

                overall_warning = True

            if details not in ("Normal", "N/A", None, "") and status == "OK":
                status = "Warning"

            parsed_check_item = HealthCheckItem(
                check_name=name,
                status=status,
                value=value,
                unit=unit,
                threshold=threshold,
                details=details,
            )
            parsed_checks.append(parsed_check_item)

            if status == "Warning":
                if details not in ("Normal", "N/A", None, ""):
                    recommendations.append(f"Check '{name}': {details}")

        except Exception as e:
            errors_encountered.append(f"Error processing check result {check}: {e}")
            overall_warning = True
            continue

    if errors_encountered:
        parsed_checks.append(
            HealthCheckItem(
                check_name="Data Retrieval/Parsing Errors",
                status="Error",
                details="; ".join(errors_encountered),
            )
        )
        overall_warning = True

    final_result: ParsedHealthCheckResult = {
        "overall_status": "Warning" if overall_warning else "OK",
        "checks": parsed_checks,
        "recommendations": recommendations,
    }
    return final_result


def parse_monitor_workload_results(
    results: Dict[str, List[Dict[str, Any]]],
) -> ParsedMonitorWorkloadResult:
    """Parses raw workload monitoring results from multiple queries into the expected MCP tool output format.

    Expects a dictionary where keys are identifiers for the source query
    (e.g., 'wlm_queue_state', 'top_queries', 'queuing_summary', etc.) and
    values are lists of dictionaries representing the raw rows returned by
    those SQL queries.

    Args:
        results: A dictionary mapping source query identifiers to lists of raw
                 result rows (as dictionaries). Expected keys include:
                 'wlm_queue_state', 'top_queries', 'queuing_summary',
                 'disk_based_query_count', 'copy_performance', 'commit_wait',
                 'current_sessions', 'wlm_apex', 'wlm_trend_hourly'.

    Returns:
        A dictionary containing structured workload details, including summaries,
        WLM state, top queries, trends, potential issues, and recommendations.
        Returns an empty dictionary if the input appears logically empty based
        on expected keys and content.
    """
    if not results or not isinstance(results, dict):
        return cast(ParsedMonitorWorkloadResult, {})

    wlm_state: List[Dict[str, Any]] = _get_list_value(results, "wlm_queue_state")
    top_queries: List[Dict[str, Any]] = _get_list_value(results, "top_queries")
    queuing_summary: List[Dict[str, Any]] = _get_list_value(results, "queuing_summary")
    disk_based_list: List[Dict[str, Any]] = _get_list_value(
        results, "disk_based_query_count"
    )
    copy_perf: List[Dict[str, Any]] = _get_list_value(results, "copy_performance")
    commit_wait_list: List[Dict[str, Any]] = _get_list_value(results, "commit_wait")
    sessions_list: List[Dict[str, Any]] = _get_list_value(results, "current_sessions")
    wlm_apex_list: List[Dict[str, Any]] = _get_list_value(results, "wlm_apex")
    wlm_trend_hourly_list: List[Dict[str, Any]] = _get_list_value(
        results, "wlm_trend_hourly"
    )

    all_extracted_lists_empty: bool = not any(
        [
            wlm_state,
            top_queries,
            queuing_summary,
            disk_based_list,
            copy_perf,
            commit_wait_list,
            sessions_list,
            wlm_apex_list,
            wlm_trend_hourly_list,
        ]
    )

    known_keys: Set[str] = {
        "wlm_queue_state",
        "top_queries",
        "queuing_summary",
        "disk_based_query_count",
        "copy_performance",
        "commit_wait",
        "current_sessions",
        "wlm_apex",
        "wlm_trend_hourly",
    }
    is_truly_empty_input: bool = True

    for k in known_keys:
        if k in results:
            v = results[k]
            if isinstance(v, list) and len(v) > 0:
                is_truly_empty_input = False
                break

    if is_truly_empty_input:
        for k, v in results.items():
            if k not in known_keys and v:
                is_truly_empty_input = False
                break

    if all_extracted_lists_empty and is_truly_empty_input:
        return cast(ParsedMonitorWorkloadResult, {})

    active_sessions_count: int = len(sessions_list)
    queries_executing: int = sum(
        q.get("num_executing", 0) for q in wlm_state if isinstance(q, dict)
    )
    queries_queued: int = sum(
        q.get("num_queued", 0) for q in wlm_state if isinstance(q, dict)
    )
    avg_commit_wait_any: Any = _get_first_value(commit_wait_list, "avg_commit_wait_ms")
    disk_based_count_any: Any = _get_first_value(disk_based_list, "disk_based_count", 0)

    avg_commit_wait: Optional[float] = (
        cast(Optional[float], avg_commit_wait_any)
        if isinstance(avg_commit_wait_any, (int, float))
        else None
    )
    disk_based_count: int = (
        cast(int, disk_based_count_any) if isinstance(disk_based_count_any, int) else 0
    )

    summary: WorkloadSummary = {
        "active_sessions": active_sessions_count,
        "queries_executing": queries_executing,
        "queries_queued": queries_queued,
        "avg_commit_wait_ms": avg_commit_wait,
        "disk_based_queries_recent": disk_based_count,
    }

    workload_trends: WorkloadTrends = {
        "apex": wlm_apex_list,
        "hourly_trend": wlm_trend_hourly_list,
    }

    potential_issues: List[str] = []
    recommendations: List[str] = []
    if disk_based_count > 0:
        issue_text: str = (
            f"{disk_based_count} queries recently executed disk-based operations. Investigate memory allocation or query complexity."
        )
        potential_issues.append(issue_text)
        recommendations.append(
            f"Consider investigating the {disk_based_count} queries that recently executed disk-based operations."
        )
    if queries_queued > 5:
        recommendations.append(
            f"High number of queued queries ({queries_queued}). Check WLM configuration and long-running queries."
        )
        potential_issues.append(f"High WLM queuing ({queries_queued} queries).")

    final_result: ParsedMonitorWorkloadResult = {
        "summary": summary,
        "wlm_state": wlm_state,
        "queue_performance": queuing_summary,
        "top_active_queries": top_queries,
        "recent_copy_performance": copy_perf,
        "workload_trends": workload_trends,
        "potential_issues": potential_issues,
        "recommendations": recommendations,
    }
    return final_result
