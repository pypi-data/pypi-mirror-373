-- Purpose: Counts the number of distinct queries that had at least one disk-based step within a specified time window.
-- Parameters: :time_window_days (integer) - The lookback period in days.
-- Source Views: STL_QUERY (for starttime), SVL_QUERY_SUMMARY (for is_diskbased)
-- Joins on: query ID
SELECT
    COUNT(DISTINCT q.query) AS disk_based_query_count
FROM
    STL_QUERY q
JOIN
    SVL_QUERY_SUMMARY qs ON q.query = qs.query
WHERE
    q.starttime >= DATEADD(day, -CAST(:time_window_days AS INT), GETDATE()) -- Filter by start time
    AND qs.is_diskbased = 't'; -- Filter for steps that went to disk (character 't')