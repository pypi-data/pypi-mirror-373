-- Purpose: Compares total queries vs. queued queries over a specified time window, grouped by hour and service class.
-- Used by: check_cluster_health tool
-- Parameters:
--   :time_window_days (integer): Lookback period in days (e.g., 1, 7).
select
    CAST(date_trunc('hour',service_class_start_time) AS DATE) as "day",
    service_class,
    count(query) as total_queries,
    sum(case when total_queue_time > 0 then 1 else 0 end) as queued_queries,
    sum(total_queue_time)/1000000/60 as q_time_mins,
    avg(datediff('ms',queue_start_time,queue_end_time)) as avg_q_ms,
    avg(datediff('ms',exec_start_time,exec_end_time)) as avg_exec_ms,
    sum(case when final_state = 'Evicted' then 1 else 0 end) as evicted
from stl_wlm_query
where service_class_start_time >= dateadd(day, -CAST(:time_window_days AS INT), CURRENT_DATE)
  and service_class > 4 
group by 1, 2
order by 1, 2;