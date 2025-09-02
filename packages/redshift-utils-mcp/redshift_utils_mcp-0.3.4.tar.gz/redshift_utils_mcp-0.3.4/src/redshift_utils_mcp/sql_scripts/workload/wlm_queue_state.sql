-- Purpose: Shows the current state of WLM queues (queued vs running queries per service class).
-- Uses stv_wlm_query_state which provides queue_time and exec_time in microseconds.
-- Parameters: None
SELECT
    service_class,
    -- Count queries currently waiting in the queue
    COUNT(CASE WHEN state IN ('Queued', 'QueuedWaiting') THEN query ELSE NULL END) AS queued_count,
    -- Count queries currently executing
    COUNT(CASE WHEN state = 'Running' THEN query ELSE NULL END) AS executing_count,
    -- Calculate max queue wait time in seconds (from microseconds)
    MAX(CASE WHEN state IN ('Queued', 'QueuedWaiting') THEN queue_time ELSE 0 END) / 1000000.0 AS max_queue_wait_seconds,
    -- Calculate max execution time in seconds (from microseconds)
    MAX(CASE WHEN state = 'Running' THEN exec_time ELSE 0 END) / 1000000.0 AS max_exec_time_seconds
FROM stv_wlm_query_state
WHERE service_class > 4 -- Exclude default system queues (1-4). Adjust if custom system queues exist or different filtering is needed.
GROUP BY service_class
ORDER BY service_class;