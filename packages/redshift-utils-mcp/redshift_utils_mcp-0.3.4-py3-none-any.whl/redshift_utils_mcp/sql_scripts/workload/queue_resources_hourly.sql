-- Purpose: Returns the per-hour resource usage per WLM queue over a specified time window.
--          Used by the 'monitor_workload' tool to analyze workload trends.
-- Parameters:
--      :time_window_days (integer) - The number of past days to include in the analysis.

SELECT
    DATE_TRUNC('hour', w.exec_start_time) AS exec_hour, -- Timestamps are UTC
    w.service_class AS "Q",
    SUM(CASE WHEN qlog.aborted = 0 THEN 1 ELSE 0 END) AS n_cp, -- Use svl_qlog.aborted for status
    SUM(CASE WHEN qlog.aborted = 1 THEN 1 ELSE 0 END) AS n_ev, -- Use svl_qlog.aborted for status
    AVG(w.total_queue_time / 1000000.0) AS avg_q_sec,
    AVG(w.total_exec_time / 1000000.0) AS avg_e_sec,
    AVG(m.query_cpu_usage_percent) AS avg_pct_cpu,
    MAX(m.query_cpu_usage_percent) AS max_pct_cpu,
    MAX(m.query_temp_blocks_to_disk) AS max_spill_mb, -- Already in MB
    SUM(m.query_temp_blocks_to_disk) AS sum_spill_mb, -- Already in MB
    SUM(m.scan_row_count) AS sum_row_scan,
    SUM(m.join_row_count) AS sum_join_rows,
    SUM(m.nested_loop_join_row_count) AS sum_nl_join_rows,
    SUM(m.return_row_count) AS sum_ret_rows,
    SUM(m.spectrum_scan_size_mb) AS sum_spec_mb
FROM
    stl_wlm_query AS w
LEFT JOIN
    svl_qlog AS qlog ON w.query = qlog.query 
LEFT JOIN
    svl_query_metrics_summary AS m ON w.query = m.query 
WHERE
    w.service_class > 4 
    AND w.exec_start_time >= DATEADD(day, -1 * CAST(:time_window_days AS INT), GETDATE())
GROUP BY
    1, 2
ORDER BY
    1 DESC, 2; -- exec_hour DESC, service_class
