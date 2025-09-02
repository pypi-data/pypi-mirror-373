-- Purpose: Summarizes query queuing activity within a specified time window, grouped by service class.
--          Provides counts, total queue time, and average queue time for queries that experienced queuing.
-- Parameters:
--   :time_window_days (integer) - The lookback period in days from the current date.

SELECT
    w.service_class                                     AS service_class,
    COUNT(w.query)                                      AS queued_query_count,
    SUM(w.total_queue_time) / 1000000                   AS total_queue_time_s,
    AVG(w.total_queue_time) / 1000000                   AS avg_queue_time_s,
    MAX(w.total_queue_time) / 1000000                   AS max_queue_time_s,
    SUM(w.total_exec_time) / 1000000                    AS total_exec_time_s,
    AVG(w.total_exec_time) / 1000000                    AS avg_exec_time_s
FROM
    stl_wlm_query w
WHERE
    w.queue_start_time >= CURRENT_DATE - (:time_window_days::integer * interval '1 day') -- Cast parameter and use interval arithmetic
    AND w.total_queue_time > 0 -- Only include queries that actually queued
    AND w.service_class > 4    -- Exclude system/internal queues (typically <= 4)
GROUP BY
    w.service_class
ORDER BY
    w.service_class;