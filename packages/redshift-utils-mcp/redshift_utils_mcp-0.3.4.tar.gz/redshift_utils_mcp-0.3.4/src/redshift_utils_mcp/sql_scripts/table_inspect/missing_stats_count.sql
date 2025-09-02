-- Purpose: Counts the number of user tables with missing or significantly stale statistics (stats_off > 10%).
-- Parameters: None
SELECT COUNT(*) AS missing_stats_count
FROM svv_table_info
WHERE schema NOT IN ('pg_catalog', 'information_schema', 'pg_internal') -- Exclude system schemas
  AND stats_off > 10.0; -- Threshold for missing/stale stats