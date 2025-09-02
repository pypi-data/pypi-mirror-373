-- Purpose: Analyzes daily trends in WLM query execution over a specified time window.
--          Aggregates query count, total/average queue time (microseconds), and total/average execution time (microseconds)
--          per day and service class.
-- Parameters: :time_window_days (integer) - The lookback period in days.

SELECT
  DATE_TRUNC('day', service_class_start_time) AS day,
  service_class,
  COUNT(query) AS query_count,
  SUM(total_queue_time) AS total_queue_time_us,
  AVG(total_queue_time)::BIGINT AS avg_queue_time_us,
  SUM(total_exec_time) AS total_exec_time_us,
  AVG(total_exec_time)::BIGINT AS avg_exec_time_us
FROM
  stl_wlm_query
WHERE
   service_class_start_time >= DATEADD(day, -CAST(:time_window_days AS INT), GETDATE()) 
  AND service_class > 4
GROUP BY
  DATE_TRUNC('day', service_class_start_time),
  service_class
ORDER BY
  day DESC,
  service_class DESC;