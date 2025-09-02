-- src/redshift_utils_mcp/sql_scripts/query_perf/overall_metrics.sql
-- Retrieves overall performance metrics for a specific query ID.
-- Uses SYS_QUERY_HISTORY joined with SVL_QUERY_METRICS_SUMMARY.
-- Used by the diagnose_query_performance tool.
-- Parameter: :query_id - The numeric ID of the query to analyze.

SELECT
    h.query_id,
    h.user_id,
    h.database_name,
    h.start_time,                                       -- Query execution start time
    h.end_time,                                         -- Query execution end time
    DATEADD(microsecond, -h.queue_time, h.start_time) AS queue_start_time, -- Calculated queue start
    h.start_time AS queue_end_time,                     -- Queue ends when execution starts
    h.execution_time,                                   -- Microseconds
    h.queue_time,                                       -- Microseconds
    m.query_cpu_time AS cpu_time,                       -- Microseconds (from metrics summary)
    m.cpu_skew,
    m.io_skew,
    m.scan_row_count,
    m.query_blocks_read AS scan_blocks_read,            -- Renamed column (from metrics summary)
    m.join_row_count,
    h.returned_rows AS return_row_count,                -- Renamed column (from history)
    m.query_temp_blocks_to_disk AS spill_size_mb,       -- Renamed column (from metrics summary)
    h.result_cache_hit,
    h.query_priority,
    h.query_type,
    h.service_class_id AS wlm_service_class_id,         -- Renamed column (from history)
    h.service_class_name AS wlm_service_class_name      -- Added service class name for clarity
    -- Note: wlm_slots is not readily available in these views.
FROM
    SYS_QUERY_HISTORY h
LEFT JOIN
    SVL_QUERY_METRICS_SUMMARY m ON h.query_id = m.query -- Join based on query ID
WHERE
    h.query_id = :query_id;