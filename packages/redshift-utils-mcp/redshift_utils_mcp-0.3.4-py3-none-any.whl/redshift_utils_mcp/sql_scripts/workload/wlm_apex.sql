-- Purpose: Calculates the peak WLM concurrency (maximum slots used simultaneously)
--          for each user-defined service class within a specified time window.
--          Also retrieves the configured concurrency and the last time queuing occurred.
--          Useful for identifying WLM bottlenecks or over-provisioning.
-- Parameters:
--      :time_window_days (integer) - The lookback period in days.

WITH query_events AS (
    -- Create events for query start (+slots) and end (-slots)
    SELECT
        service_class,
        slot_count,
        service_class_start_time AS event_time,
        1 AS event_type -- 1 for start
    FROM stl_wlm_query
    WHERE service_class > 4 -- Exclude system queues (typically 1-4)
      AND userid > 1 -- Exclude system users
      AND service_class_start_time >= GETDATE() - (:time_window_days::integer * interval '1 day') -- Cast parameter and use interval arithmetic
    UNION ALL
    SELECT
        service_class,
        slot_count,
        service_class_end_time AS event_time,
        -1 AS event_type -- -1 for end
    FROM stl_wlm_query
    WHERE service_class > 4
      AND userid > 1
      AND service_class_end_time >= GETDATE() - (:time_window_days::integer * interval '1 day') -- Cast parameter and use interval arithmetic
      AND service_class_end_time IS NOT NULL -- Ensure end time exists for calculation
),
concurrency_timeline AS (
    -- Calculate the running total of slots used at each event time
    SELECT
        service_class,
        event_time,
        SUM(slot_count * event_type) OVER (PARTITION BY service_class ORDER BY event_time, event_type ROWS UNBOUNDED PRECEDING) AS current_slots_used
    FROM query_events
),
peak_concurrency AS (
    -- Find the maximum concurrent slots used for each service class in the window
    SELECT
        service_class,
        MAX(current_slots_used) AS max_concurrent_slots
    FROM concurrency_timeline
    GROUP BY service_class
),
last_queued AS (
    -- Find the last time queuing occurred for each service class in the window
    SELECT
        service_class,
        MAX(queue_end_time) AS last_queued_time
    FROM stl_wlm_query
    WHERE service_class > 4
      AND userid > 1
      AND total_queue_time > 0
      AND queue_start_time >= GETDATE() - (:time_window_days::integer * interval '1 day') -- Cast parameter and use interval arithmetic
    GROUP BY service_class
),
config AS (
    -- Get the configured concurrency level for each service class
    SELECT DISTINCT service_class, num_query_tasks
    FROM stv_wlm_service_class_config
    WHERE service_class > 4
)
-- Final result: Combine peak concurrency, last queued time, and configured concurrency
SELECT
    pc.service_class,
    cfg.num_query_tasks AS configured_concurrency, -- Configured max slots
    NVL(pc.max_concurrent_slots, 0) AS max_observed_concurrency, -- Actual peak slots used
    lq.last_queued_time
FROM peak_concurrency pc
LEFT JOIN last_queued lq ON pc.service_class = lq.service_class
LEFT JOIN config cfg ON pc.service_class = cfg.service_class
WHERE pc.service_class IS NOT NULL -- Filter out potential nulls if no activity
ORDER BY pc.service_class;