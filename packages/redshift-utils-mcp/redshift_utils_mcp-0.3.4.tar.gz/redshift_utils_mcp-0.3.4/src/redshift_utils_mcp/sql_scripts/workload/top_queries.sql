-- Purpose: Identifies the top N queries based on total execution time (queue + execution)
--          within a specified time window for completed queries. Returns key performance metrics.
-- History:
-- 2024-04-26: Adapted from older top_queries.sql, using svl_query_summary for richer metrics.
-- 2025-04-27: Corrected to use STL_WLM_QUERY for timing and SVL_QUERY_METRICS for CPU/Spill/IO/Rows.
--             Grouping by MD5(querytxt) might be inaccurate for very long queries due to truncation in STL_QUERY.
-- Parameters:
--   :time_window_days (integer): Lookback period in days from the current date.
--   :top_n_queries (integer): Number of top queries to return based on total time.

WITH query_metrics AS (
    -- Select query-level metrics (segment=0)
    SELECT
        query,
        MAX(query_cpu_time) AS query_cpu_time, -- CPU time in seconds
        MAX(query_temp_blocks_to_disk) AS query_spill_mb, -- Spill in MB
        MAX(query_blocks_read) AS query_blocks_read, -- Blocks read (1MB)
        MAX(return_row_count) AS return_row_count -- Rows returned
    FROM svl_query_metrics
    WHERE segment = 0 -- Aggregate metrics are at segment 0
    GROUP BY query
)
SELECT
    COUNT(q.query) AS n_qry,
    MAX(SUBSTRING(TRIM(q.querytxt), 1, 80)) AS qrytext, -- Query text snippet
    SUM(w.total_queue_time + w.total_exec_time) / 1000000.0 AS total_time_secs, -- Total time (queue + exec) in seconds (from STL_WLM_QUERY)
    AVG(w.total_queue_time + w.total_exec_time) / 1000000.0 AS avg_time_secs, -- Average time in seconds (from STL_WLM_QUERY)
    SUM(COALESCE(qm.query_cpu_time, 0)) AS total_cpu_secs, -- Total CPU time in seconds (from SVL_QUERY_METRICS)
    SUM(COALESCE(qm.query_spill_mb, 0)) AS total_spill_mb, -- Total spill to disk in MB (from SVL_QUERY_METRICS)
    SUM(COALESCE(qm.query_blocks_read, 0)) AS total_blocks_read, -- Total blocks read (1MB) (from SVL_QUERY_METRICS)
    SUM(COALESCE(qm.return_row_count, 0)) AS total_rows_returned, -- Total rows returned (from SVL_QUERY_METRICS)
    MAX(q.query) AS max_query_id, -- Example query ID for this group
    MAX(q.starttime)::DATE AS last_run_date, -- Last date this query text ran
    MD5(TRIM(q.querytxt)) AS qry_md5 -- MD5 hash for grouping identical queries (potential truncation issue)
FROM
    stl_query q
JOIN
    stl_wlm_query w ON q.query = w.query -- Join for accurate timing metrics
LEFT JOIN
    query_metrics qm ON q.query = qm.query -- Join for CPU, spill, IO, row metrics
WHERE
    q.userid > 1 -- Exclude system users (userid=1)
    AND q.starttime >= DATEADD(day, -1 * :time_window_days, CURRENT_DATE) -- Filter by time window
    AND q.aborted = 0 -- Consider only successfully completed queries
GROUP BY
    qry_md5 -- Group identical queries together
ORDER BY
    total_time_secs DESC -- Rank by total time spent (queue + execution)
LIMIT :top_n_queries; -- Limit to the top N queries