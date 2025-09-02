-- Purpose: Retrieves the full text of a specific query ID from stl_querytext.
--          Handles multi-part queries stored across multiple rows.
-- Parameters:
--   :query_id (integer): The ID of the query.
SELECT
    LISTAGG(CASE WHEN LEN(RTRIM(text)) = 0 THEN text ELSE RTRIM(text) END, '') WITHIN GROUP (ORDER BY sequence) AS query_text
FROM stl_querytext
WHERE query = :query_id
GROUP BY query; -- Grouping by query is necessary for LISTAGG