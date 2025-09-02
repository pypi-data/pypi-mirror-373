-- Purpose: Analyzes hourly trends in WLM query execution over a specified time window.
--          Aggregates query count, total/average queue time (microseconds), and total/average execution time (microseconds)
--          per hour and service class.
-- Parameters: :time_window_days (integer) - The lookback period in days.

SELECT
    DATE_TRUNC('hour', service_class_start_time) AS hour, -- Group by hour
    service_class,
    COUNT(query) AS query_count,
    SUM(total_queue_time) AS total_queue_time_us,
    AVG(total_queue_time)::BIGINT AS avg_queue_time_us, -- Cast AVG to BIGINT
    SUM(total_exec_time) AS total_exec_time_us,
    AVG(total_exec_time)::BIGINT AS avg_exec_time_us -- Cast AVG to BIGINT
FROM
    stl_wlm_query
WHERE
    -- Use CURRENT_TIMESTAMP (standard) and DATEADD for interval calculation
    service_class_start_time >= CURRENT_TIMESTAMP - (:time_window_days::integer * interval '1 day') -- Use interval arithmetic
    AND service_class > 4 -- Exclude system/internal queues (typically <= 4)
GROUP BY
    DATE_TRUNC('hour', service_class_start_time), -- Group by hour
    service_class
ORDER BY
    hour DESC,
    service_class DESC;