-- Purpose: Counts the number of user tables likely needing VACUUM due to high unsorted percentage (> 10%).
-- Parameters: None
-- Note: svv_table_info filters system tables, but explicit exclusion is kept for clarity.
--       Threshold lowered from 20% to 10% based on general performance recommendations.
SELECT COUNT(*) AS needs_vacuum_count
FROM svv_table_info
WHERE schema NOT IN ('pg_catalog', 'information_schema', 'pg_internal') -- Exclude system schemas (using correct 'schema' column)
  AND unsorted > 10.0; -- Recommended threshold for needing vacuum is often 5-10%