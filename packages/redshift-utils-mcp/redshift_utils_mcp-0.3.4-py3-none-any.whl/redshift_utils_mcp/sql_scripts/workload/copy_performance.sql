-- Purpose: Analyze the performance and errors of COPY commands executed within a specified time window.
--          Summarizes metrics like total duration, rows loaded, size (MB), throughput (MB/s),
--          file count, and error count per COPY command.
-- Source: Combines stl_query for overall timing and stl_copy_summary for load details.
-- Parameters: :time_window_days (integer) - The lookback period in days.

select q.starttime,
       s.query,
       substring(q.querytxt, 1, 120)                            as querytxt,
       s.n_files,
       size_mb,
       s.time_seconds,
       s.size_mb / decode(s.time_seconds, 0, 1, s.time_seconds) as mb_per_s
from (select query,
             count(*)                           as n_files,
             sum(transfer_size / (1024 * 1024)) as size_MB,
             (max(end_Time) -
              min(start_Time)) / (1000000)      as time_seconds,
             max(end_time)                      as end_time
      from stl_s3client
      where http_method = 'GET'
        and query > 0
        and transfer_time > 0
      group by query) as s
         LEFT JOIN stl_Query as q on q.query = s.query
where s.end_Time >= dateadd(day, -1 * :time_window_days, current_date)
order by s.time_Seconds desc, size_mb desc, s.end_time desc
limit 50;