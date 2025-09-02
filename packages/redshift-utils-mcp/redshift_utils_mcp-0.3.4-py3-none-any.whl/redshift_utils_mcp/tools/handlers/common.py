"""Shared TypedDicts, Exceptions, and Imports for tool handlers."""

from typing import Dict, Any, List, Optional, Union
from typing_extensions import TypedDict


class QueryNotFound(Exception):
    """Custom exception for when a specific query ID is not found."""

    pass


class TableNotFound(Exception):
    """Custom exception for when a specific table is not found."""

    pass


class ExecuteAdHocQuerySuccessResult(TypedDict):
    status: str
    columns: List[Dict[str, Any]]
    rows: List[Dict[str, Any]]
    row_count: int


class ExecuteAdHocQueryErrorResult(TypedDict):
    status: str
    error_message: str
    error_type: str


ExecuteAdHocQueryResult = Union[
    ExecuteAdHocQuerySuccessResult, ExecuteAdHocQueryErrorResult
]


class ClusterStatus(TypedDict):
    underrepped_blocks: int


class ResourceUtilization(TypedDict):
    cpu_summary: str
    memory_summary: str
    disk_used_pct: float


class CurrentActivity(TypedDict):
    running_queries_count: int
    longest_running_query_secs: int
    lock_contention_summary: str


class WLMQueueSummary(TypedDict):
    service_class: int
    slots: int
    queued: int
    executing: int


class WLMStatus(TypedDict):
    queue_summary: List[WLMQueueSummary]
    recent_queue_wait_summary: str
    max_commit_wait_secs: int


class BasicTableHealth(TypedDict):
    missing_stats_count: int
    stale_stats_count: int
    needs_vacuum_count: int


class FullTableDesignHealth(TypedDict, total=False):
    no_sort_key_count: int
    compressed_sort_key_count: int
    no_compression_count: int
    dist_skew_count: int


class FullTableMaintenanceHealth(TypedDict, total=False):
    vacuum_status_summary: str
    tombstone_count: int


class FullPerformanceIndicators(TypedDict, total=False):
    copy_issue_summary: str
    top_alerts: List[Dict[str, Any]]


class CheckClusterHealthResult(TypedDict):
    check_level: str
    timestamp: str
    cluster_status: ClusterStatus
    resource_utilization: ResourceUtilization
    current_activity: CurrentActivity
    wlm_status: WLMStatus
    basic_table_health: BasicTableHealth
    full_table_design_health: Optional[FullTableDesignHealth]
    full_table_maintenance_health: Optional[FullTableMaintenanceHealth]
    full_performance_indicators: Optional[FullPerformanceIndicators]
    recommendations: List[str]
    errors: Optional[List[Dict[str, str]]]


class QueryPerformanceMetrics(TypedDict):
    execution_time_secs: Optional[float]
    queue_time_secs: Optional[float]
    cpu_time_secs: Optional[float]
    read_io_mb: Optional[float]
    spill_mb: Optional[float]
    rows_processed: Optional[int]


class QueryStepSummary(TypedDict):
    step_label: str
    duration_secs: float
    is_disk_based: bool
    memory_mb: float
    rows: int


class SliceSkewSummary(TypedDict):
    segment: int
    slice: int
    max_rows: int
    max_cpu_secs: float
    skew_rows_ratio: float
    skew_cpu_ratio: float


class HistoricalComparison(TypedDict, total=False):
    average_duration_secs: float
    runs_analyzed: int
    performance_trend: str


class DiagnoseQueryPerformanceSuccessResult(TypedDict):
    query_id: int
    query_text_snippet: str
    execution_plan_summary: str
    performance_metrics: QueryPerformanceMetrics
    step_summary: List[QueryStepSummary]
    slice_skew_summary: List[SliceSkewSummary]
    alerts: List[Dict[str, Any]]
    historical_comparison: Optional[HistoricalComparison]
    potential_issues: List[str]
    recommendations: List[str]
    errors: Optional[List[Dict[str, str]]]


class DiagnoseQueryPerformanceErrorResult(TypedDict):
    status: str
    error_message: str
    error_type: str


DiagnoseQueryPerformanceResult = Union[
    DiagnoseQueryPerformanceSuccessResult, DiagnoseQueryPerformanceErrorResult
]


class TableDesign(TypedDict):
    diststyle: Optional[str]
    distkey: Optional[str]
    sortkeys: List[str]
    has_pk: bool
    has_fk: bool
    max_varchar_size: Optional[int]
    encoding_summary: Dict[str, int]


class TableStorage(TypedDict):
    size_mb: Optional[float]
    row_count: Optional[int]
    dist_skew_ratio: Optional[float]
    block_skew_ratio: Optional[float]
    pct_slices_populated: Optional[float]


class TableHealth(TypedDict):
    stats_off_pct: Optional[float]
    unsorted_pct: Optional[float]
    last_vacuum_time: Optional[str]


class TableUsage(TypedDict):
    scan_frequency: Optional[str]
    last_scan_time: Optional[str]
    scan_details_summary: Optional[str]
    recent_alert_count: int


class InspectTableSuccessResult(TypedDict):
    schema_name: str
    table_name: str
    table_id: int
    design: TableDesign
    storage: TableStorage
    health_and_maintenance: TableHealth
    usage_and_activity: TableUsage
    recommendations: List[str]
    errors: Optional[List[Dict[str, str]]]


class InspectTableErrorResult(TypedDict):
    status: str
    error_message: str
    error_type: str


InspectTableResult = Union[InspectTableSuccessResult, InspectTableErrorResult]


class ContentionDetail(TypedDict):
    type: str
    blocking_pid: Optional[int]
    waiting_pid: Optional[int]
    locked_object_name: Optional[str]
    lock_mode: Optional[str]
    duration_secs: float
    waiting_pids_list: List[int]


class DiagnoseLocksResult(TypedDict):
    contention_details: List[ContentionDetail]
    summary: str


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


class GetTableDefinitionSuccessResult(TypedDict):
    status: str
    ddl: str


class GetTableDefinitionErrorResult(TypedDict):
    status: str
    error_message: str
    error_type: str


GetTableDefinitionResult = Union[
    GetTableDefinitionSuccessResult, GetTableDefinitionErrorResult
]
