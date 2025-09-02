-- Purpose: Summarizes WLM queuing activity (counts, average/max/total wait times) per service class over a specified time window.
-- Parameters:
--   :time_window_days (integer): Lookback period in days (e.g., 1, 7).
SELECT
    service_class,
    COUNT(*) AS total_queued_queries,
    AVG(total_queue_time / 1000000.0) AS avg_queue_time_seconds,
    MAX(total_queue_time / 1000000.0) AS max_queue_time_seconds,
    SUM(total_queue_time / 1000000.0) AS total_queue_time_seconds
FROM stl_wlm_query
WHERE service_class > 4 -- Exclude system queues (adjust if needed)
  AND queue_start_time >= DATEADD(day, -1 * CAST(:time_window_days AS INT), GETDATE()) -- Use parameter with DATEADD
  AND total_queue_time > 0 -- Only include queries that actually queued
GROUP BY service_class
ORDER BY total_queued_queries DESC;