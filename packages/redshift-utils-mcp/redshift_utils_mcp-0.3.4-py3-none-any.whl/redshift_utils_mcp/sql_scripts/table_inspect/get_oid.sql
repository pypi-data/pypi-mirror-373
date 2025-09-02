-- Purpose: Retrieves the Object ID (OID) for a given table.
-- This OID is often used in subsequent queries against system catalogs
-- that reference tables by their OID instead of name.
--
-- Parameters:
--   :schema_name - The name of the schema containing the table.
--   :table_name - The name of the table.
--
-- Returns: A single row with the 'oid' column if the table exists, otherwise no rows.

SELECT
    c.oid
FROM
    pg_class c
JOIN
    pg_namespace n ON n.oid = c.relnamespace
WHERE
    n.nspname = :schema_name
    AND c.relname = :table_name;