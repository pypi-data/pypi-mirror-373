-- Purpose: Retrieve a list of user-defined schema names from the Redshift cluster.
-- This script is used by the 'schema_list' resource handler.
-- Filters out system schemas by checking the owner ID (schema_owner > 1).
-- Uses the Redshift-specific SVV_ALL_SCHEMAS view.
SELECT schema_name
FROM svv_all_schemas
WHERE schema_owner > 1
ORDER BY schema_name;