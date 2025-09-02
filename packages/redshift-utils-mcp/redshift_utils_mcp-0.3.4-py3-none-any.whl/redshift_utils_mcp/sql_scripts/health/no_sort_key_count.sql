-- Purpose: Counts the number of user tables that do not have a sort key defined.
-- Parameters: None
-- Corrected based on SVV_TABLE_INFO documentation (using sortkey_num).
SELECT COUNT(*) AS no_sort_key_count
FROM svv_table_info ti
WHERE ti.schema NOT IN ('pg_catalog', 'information_schema', 'pg_internal') -- Exclude system schemas
  AND ti."temporary" = false -- Exclude temporary tables
  AND ti.sortkey_num = 0; -- Check if the number of sort keys is 0