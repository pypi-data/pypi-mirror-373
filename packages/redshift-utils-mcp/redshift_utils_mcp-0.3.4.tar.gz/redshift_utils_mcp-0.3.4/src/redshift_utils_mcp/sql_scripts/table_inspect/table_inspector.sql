-- Name: table_inspector
-- Description: Retrieves detailed column information for a specific table, including data type, nullability,
-- defaults, encoding, distkey, sortkey, and remarks by joining pg_catalog tables and pg_table_def.
-- Parameters:
--   - schema_name: The name of the schema.
--   - table_name: The name of the table.
-- Returns: Table columns with their attributes.

SELECT 
    table_schema,
    table_name,
    column_name,
    ordinal_position,
    data_type,
    character_maximum_length,
    numeric_precision,
    numeric_scale,
    is_nullable
FROM 
    SVV_COLUMNS
WHERE 
    table_schema = :schema_name -- Filter by schema name
    AND table_name = :table_name -- Filter by table name
ORDER BY 
    ordinal_position;