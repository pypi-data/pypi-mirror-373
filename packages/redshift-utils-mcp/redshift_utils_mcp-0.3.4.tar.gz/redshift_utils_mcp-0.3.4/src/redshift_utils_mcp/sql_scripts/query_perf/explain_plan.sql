-- Purpose: Retrieves the execution plan steps for a specific query ID.
-- Parameters:
--   :query_id (integer): The ID of the query.
SELECT
    plannode,
    info
FROM stl_explain
WHERE query = :query_id
ORDER BY plannode; -- Order by step number