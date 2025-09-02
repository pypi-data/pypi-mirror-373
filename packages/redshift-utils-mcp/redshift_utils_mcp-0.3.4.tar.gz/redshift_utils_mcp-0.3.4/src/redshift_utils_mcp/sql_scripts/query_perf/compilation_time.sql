-- Purpose: Retrieves compilation time details for each segment of a specific query from SVL_COMPILE.
--          Helps identify potential bottlenecks during the query compilation phase.
-- Note: SVL_COMPILE does not contain error messages or step-level detail beyond segments.
-- Parameters:
--   %(query_id)s - The numeric ID of the query to analyze.

SELECT
    query,
    segment,
    locus, -- Location code (1 for compute node, 2 for leader node)
    starttime,
    endtime,
    datediff(microsecond, starttime, endtime) AS compile_time_microseconds -- Time spent compiling this segment
FROM
    svl_compile
WHERE
    query = :query_id -- Changed from %(query_id)s to :query_id for Data API compatibility
ORDER BY
    query,
    segment;