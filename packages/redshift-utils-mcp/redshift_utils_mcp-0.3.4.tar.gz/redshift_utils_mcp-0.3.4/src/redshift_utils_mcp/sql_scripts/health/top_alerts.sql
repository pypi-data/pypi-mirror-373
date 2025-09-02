-- Purpose: Retrieves recent performance alerts from stl_alert_event_log within a specified time window.
-- Parameters:
--   :time_window_days (integer): Lookback period in days (e.g., 1, 7).
SELECT t.schema AS SCHEMA,
       trim(s.perm_table_name) AS TABLE,
       (sum(abs(datediff(seconds, coalesce(b.starttime,d.starttime,s.starttime), CASE WHEN coalesce(b.endtime,d.endtime,s.endtime) > coalesce(b.starttime,d.starttime,s.starttime) THEN coalesce(b.endtime,d.endtime,s.endtime) ELSE coalesce(b.starttime,d.starttime,s.starttime) END)))/60)::numeric(24,0) AS minutes,
       sum(coalesce(b.rows,d.rows,s.rows)) AS ROWS,
       trim(split_part(l.event,':',1)) AS event,
       substring(trim(l.solution),1,60) AS solution,
       max(l.query) AS sample_query,
       count(DISTINCT l.query),
       q.text AS query_text
FROM stl_alert_event_log AS l
LEFT JOIN stl_scan AS s ON s.query = l.query
AND s.slice = l.slice
AND s.segment = l.segment
LEFT JOIN stl_dist AS d ON d.query = l.query
AND d.slice = l.slice
AND d.segment = l.segment
LEFT JOIN stl_bcast AS b ON b.query = l.query
AND b.slice = l.slice
AND b.segment = l.segment
LEFT JOIN
  (SELECT query,
          LISTAGG(text) WITHIN
   GROUP (
          ORDER BY sequence) AS text
   FROM stl_querytext
   WHERE sequence < 100
   GROUP BY query) AS q ON q.query = l.query
LEFT JOIN svv_table_info AS t ON t.table_id = s.tbl
WHERE l.userid >1
  AND l.event_time >= dateadd(DAY, -CAST(:time_window_days AS INT) , CURRENT_DATE)
  AND s.perm_table_name NOT LIKE 'volt_tt%'
  AND SCHEMA IS NOT NULL
GROUP BY 1,
         2,
         5,
         6,
         query_text
ORDER BY 3 DESC, 7 DESC;