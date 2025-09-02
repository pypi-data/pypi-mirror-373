-- Purpose: Retrieve key table metrics using the svv_table_info system view.
--          Provides information on table design, storage, and health.
-- Parameters:
--   :schema_name - The name of the schema containing the table.
--   :table_name  - The name of the table to inspect.
SELECT
    "schema",                   -- Schema name
    "table",                    -- Table name
    table_id,                   -- Table OID
    diststyle,                  -- Distribution style (EVEN, KEY, ALL, AUTO)
    sortkey1,                   -- First sort key column
    sortkey1_enc,               -- Encoding of the first sort key
    size AS size_mb,            -- Table size in megabytes
    tbl_rows,                   -- Total number of rows
    skew_sortkey1,              -- Skew based on the first sort key (if applicable)
    skew_rows,                  -- Skew based on data distribution across slices
    stats_off,                  -- Percentage indicating staleness of statistics
    unsorted,                   -- Percentage of unsorted rows (relevant for VACUUM)
    estimated_visible_rows,     -- Estimated rows visible to the current transaction
    max_varchar                 -- Size of the largest VARCHAR column
FROM
    svv_table_info
WHERE
    "schema" = :schema_name
    AND "table" = :table_name;