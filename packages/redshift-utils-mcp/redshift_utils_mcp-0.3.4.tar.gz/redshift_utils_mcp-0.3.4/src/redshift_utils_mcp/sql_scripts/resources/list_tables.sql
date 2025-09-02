-- Purpose: Retrieves a list of table names within a specified schema using the recommended Redshift view.
-- Parameters:
--   :schema_param (text) - The name of the schema to list tables from.

SELECT table_name
FROM svv_tables
WHERE table_schema = :schema_param
ORDER BY table_name;