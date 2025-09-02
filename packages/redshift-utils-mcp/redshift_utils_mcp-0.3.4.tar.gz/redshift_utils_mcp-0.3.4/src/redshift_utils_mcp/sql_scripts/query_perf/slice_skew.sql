-- Purpose: Identifies query segments with significant execution time skew across slices.
--          Helps diagnose performance issues caused by uneven workload distribution.
-- Parameter: :query_id - The numeric ID of the Redshift query to analyze.
-- Source: Adapted from AWS Redshift documentation and best practices. Uses svl_query_report.elapsed_time.
-- Output Columns:
--   segment: The query segment number.
--   min_duration_ms: Minimum duration (in milliseconds) for any slice within this segment.
--   max_duration_ms: Maximum duration (in milliseconds) for any slice within this segment.
--   avg_duration_ms: Average duration (in milliseconds) across all slices within this segment.
--   duration_spread_ms: Difference between max and min duration within the segment.
--   pct_skew: Percentage skew calculated as (spread / avg_duration) * 100. High values indicate significant skew.

WITH segment_slice_times AS (
  SELECT -- Calculate total execution time per slice within each segment
    query,
    segment,
    slice,
    -- SUM(rows) as rows, -- Included for potential future analysis, though not used in final skew calc
    -- DATEDIFF measures wall-clock time from first step start to last step end for the group.
    -- SUM(elapsed_time) measures the total execution time for all steps in the group.
    -- elapsed_time is in microseconds, convert to milliseconds.
    SUM(elapsed_time) / 1000.0 AS duration_ms
  FROM svl_query_report
  WHERE query = :query_id
  GROUP BY query, segment, slice
)
SELECT
  segment,
  MIN(duration_ms) as min_duration_ms,
  MAX(duration_ms) as max_duration_ms,
  AVG(duration_ms) as avg_duration_ms,
  MAX(duration_ms) - MIN(duration_ms) as duration_spread_ms,
  -- Avoid division by zero if avg_duration_ms is 0
  CASE
    WHEN AVG(duration_ms) = 0 THEN 0
    ELSE ROUND((MAX(duration_ms)::decimal - MIN(duration_ms)::decimal) * 100.0 / AVG(duration_ms), 2)
  END as pct_skew
FROM segment_slice_times
GROUP BY segment
ORDER BY duration_spread_ms DESC;