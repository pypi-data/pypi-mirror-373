-- Purpose: Identifies the top 10 longest-running queries against a specific table
-- by analyzing query execution history and performance metrics.
-- Used for performance troubleshooting and query optimization.
--
-- Parameters:
-- s.id - The table name or ID to inspect (currently set to 'sff_analytics_delivery_cost_metrics')
--
-- This query joins multiple system tables to collect:
-- - Query execution times and duration
-- - Table information
-- - User details
-- - Performance metrics (rows processed, disk usage)
--
-- The results help identify potentially problematic queries that might
-- benefit from optimization or tuning.

SELECT
 DISTINCT
q.query AS query_id,
q.starttime,
q.endtime,
DATEDIFF(seconds, q.starttime, q.endtime) AS duration_seconds,
s.name AS table_name,
qm.rows,
qm.blocks_to_disk AS disk_blocks_used,
qm.max_blocks_to_disk AS max_disk_blocks_used,
u.usename AS username,
TRIM(q.querytxt) AS query_text
FROM
 stl_query q
JOIN
 stl_scan sc ON q.query = sc.query
JOIN
 stv_tbl_perm s ON sc.tbl = s.id
JOIN
 pg_user u ON q.userid = u.usesysid
LEFT JOIN
 stl_query_metrics qm ON q.query = qm.query AND qm.segment = -1 AND qm.step_type = -1
WHERE
s.id = :table_id -- Filter by the specific table OID
ORDER BY
 duration_seconds DESC
LIMIT 10;