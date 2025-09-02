-- Purpose: Retrieves information about currently active sessions and their running queries (using stv_inflight for real-time view).
-- Parameters: None
SELECT
    s.process AS session_pid,
    s.user_name,
    s.db_name,
    i.text AS current_query_snippet, -- Truncated query text from stv_inflight
    i.starttime AS query_start_time,
    CASE
        WHEN i.starttime IS NOT NULL THEN TRUNC(DATEDIFF(second, i.starttime, GETDATE()))
        ELSE NULL
    END AS query_duration_seconds
FROM stv_sessions s
LEFT JOIN stv_inflight i ON s.process = i.pid -- Join on inflight queries for the session
WHERE s.user_name <> 'rdsdb' -- Exclude internal users
  AND (i.text IS NULL OR ( -- Apply text filters only if a query is running
        i.text NOT LIKE 'padb_fetch_sample:%'
    AND i.text NOT LIKE 'SELECT current_setting%'
    ))
ORDER BY query_duration_seconds DESC NULLS LAST; -- Show longest running first, then sessions without active queries