-- Purpose: Retrieves alert events logged for a specific query ID from stl_alert_event_log.
--          Used by the diagnose_query_performance tool to identify potential issues
--          like missing statistics, very selective filters, etc., related to the query execution.
-- Parameter: :query_id - The numeric ID of the query to fetch alerts for.

SELECT
    event_time,      -- Timestamp when the alert event occurred
    solution,        -- Suggested solution for the alert
    event,           -- Description of the alert event (e.g., 'Missing statistics', 'Very selective query filter')
    query,           -- The query ID itself
    userid,          -- User ID who ran the query
    pid              -- Process ID of the backend process for the query
FROM
    stl_alert_event_log
WHERE
    query = :query_id -- Match stl_alert_event_log.query type (integer)
ORDER BY
    event_time;