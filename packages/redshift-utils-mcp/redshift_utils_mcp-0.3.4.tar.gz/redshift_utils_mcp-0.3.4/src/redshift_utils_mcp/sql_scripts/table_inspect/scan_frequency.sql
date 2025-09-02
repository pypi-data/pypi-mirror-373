-- Purpose: Analyzes the scan frequency for a specific table based on stl_scan logs in the last 10 days.
--          Provides total scan count, counts for the last day and 7 days, and the last scan time.
--          Used by the 'inspect_table' tool.
-- :table_id: The OID (Object ID) of the table to inspect.

SELECT
    MAX(s.starttime) AS last_scan_time,
    COUNT(DISTINCT CASE WHEN s.starttime >= GETDATE() - interval '1 day' THEN s.query ELSE NULL END) AS scan_count_last_day,
    COUNT(DISTINCT CASE WHEN s.starttime >= GETDATE() - interval '7 days' THEN s.query ELSE NULL END) AS scan_count_last_7_days,
    COUNT(DISTINCT s.query) AS total_scan_count
FROM
    stl_scan s
WHERE
    s.tbl = :table_id
    AND s.userid > 1                           -- Exclude system users
    AND s.perm_table_name NOT IN ('Internal Worktable','S3') -- Exclude internal/temp tables
    -- Optional: Add a time window filter on starttime if stl_scan is very large and performance is an issue,
    -- but the CASE statements should be reasonably efficient for recent data.
    AND s.starttime >= GETDATE() - interval '10 days' -- Example: Limit scan to last 30 days