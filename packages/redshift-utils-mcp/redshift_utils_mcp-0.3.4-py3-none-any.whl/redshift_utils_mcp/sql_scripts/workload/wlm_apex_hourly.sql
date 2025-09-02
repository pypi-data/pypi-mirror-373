-- Purpose: Calculates the peak WLM concurrency (maximum slots used simultaneously)
--          per hour for each user-defined service class within a specified time window.
--          Useful for understanding hourly WLM pressure and potential bottlenecks.
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
    -- Calculate the running total of slots used at each event time, partitioning by service class
    SELECT
        service_class,
        event_time,
        -- Extract the hour for grouping later
        DATE_TRUNC('hour', event_time) AS event_hour,
        -- Calculate running total of slots for the service class up to this event
        SUM(slot_count * event_type) OVER (PARTITION BY service_class ORDER BY event_time, event_type ROWS UNBOUNDED PRECEDING) AS current_slots_used
    FROM query_events
),
peak_hourly_concurrency AS (
    -- Find the maximum concurrent slots used for each service class within each hour
    SELECT
        service_class,
        event_hour,
        MAX(current_slots_used) AS max_concurrent_slots_in_hour
    FROM concurrency_timeline
    GROUP BY service_class, event_hour
)
-- Final result: Show the peak concurrency for each service class per hour
SELECT
    phc.event_hour,
    phc.service_class,
    NVL(phc.max_concurrent_slots_in_hour, 0) AS max_observed_concurrency_in_hour
FROM peak_hourly_concurrency phc
WHERE phc.service_class IS NOT NULL -- Filter out potential nulls if no activity
ORDER BY phc.event_hour, phc.service_class;