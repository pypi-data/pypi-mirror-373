-- Purpose: Counts the number of user tables with significant distribution skew (skew_rows > 4).
-- Parameters: None
SELECT COUNT(*) AS dist_skew_count
FROM svv_table_info
WHERE schema NOT IN ('pg_catalog', 'information_schema', 'pg_internal') -- Exclude system schemas (though svv_table_info often does this implicitly)
  -- Note: svv_table_info does not include temporary tables, so no explicit filter needed.
  AND skew_rows > 4; -- Common threshold for significant distribution skew