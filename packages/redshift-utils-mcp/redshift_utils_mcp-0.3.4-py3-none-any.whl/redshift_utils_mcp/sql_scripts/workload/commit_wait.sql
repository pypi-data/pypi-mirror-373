-- Purpose: Finds the maximum commit queue wait time (time between entering queue and starting commit) in seconds over a specified time window.
-- Uses DATEDIFF(ms, startqueue, startwork) based on STL_COMMIT_STATS documentation.
-- Parameters:
--   :time_window_days (integer): Lookback period in days (e.g., 1, 7).
SELECT
    MAX(DATEDIFF(ms, startqueue, startwork) / 1000.0) AS max_commit_wait_seconds
FROM stl_commit_stats
WHERE startqueue >= DATEADD(day, -CAST(:time_window_days AS INT), GETDATE()); -- Use parameter and DATEADD