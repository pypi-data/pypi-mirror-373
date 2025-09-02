-- Purpose: Counts the number of user tables with stale statistics (stats_off > 10).
-- Source: Based on AWS Redshift best practices using svv_table_info.stats_off
-- Parameters: None
SELECT COUNT(*) AS stale_stats_count
FROM svv_table_info
WHERE schema NOT IN ('pg_catalog', 'information_schema', 'pg_internal') -- Exclude system schemas. Use 'schema' column name.
  AND stats_off > 10; -- Standard threshold for staleness