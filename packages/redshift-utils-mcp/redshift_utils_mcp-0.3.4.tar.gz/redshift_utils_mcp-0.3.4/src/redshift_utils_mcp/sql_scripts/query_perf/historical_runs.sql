-- Find historical runs of the same query text as the given query_id using SYS_QUERY_HISTORY.
-- Uses user_query_hash for accurate matching of full query text.
-- Parameters:
--   :query_id - The ID of the query to find historical runs for.
--   :historical_limit - The maximum number of historical runs to return (default: 10).

WITH target_query AS (
    -- Get the user_query_hash of the target query's text
    SELECT user_query_hash
    FROM sys_query_history
    WHERE query_id = :query_id
    LIMIT 1 -- Should be unique, but just in case
)
SELECT
    h.user_id,
    h.query_id,
    h.service_class_name, -- Note: May be empty on Serverless
    h.start_time,
    h.end_time,
    h.queue_time / 1000000.0      AS queue_seconds,
    h.execution_time / 1000000.0  AS exec_seconds,
    CASE
        WHEN h.status = 'failed' THEN 1
        WHEN h.status = 'canceled' THEN 1
        ELSE 0
    END                           AS aborted, -- Map status to 0/1 like original script
    h.status                      AS final_state, -- Use the direct status from sys_query_history
    h.compute_type,               -- Replaces concurrency_scaling_status
    LEFT(REGEXP_REPLACE(h.query_text, '[\\n\\t]+', ' '), 80) AS query_text_snippet -- Use query_text (still truncated at 4000)
FROM sys_query_history h
JOIN target_query tq ON h.user_query_hash = tq.user_query_hash
WHERE h.user_id > 1 -- Exclude system queries
  AND h.query_id != :query_id -- Exclude the original query itself
ORDER BY h.start_time DESC
LIMIT :historical_limit;