-- Purpose: List tables used in running transactions and the type of lock granted to it.
select
  current_time,
  c.relnamespace,
  c.relname,
  l.database,
  l.transaction,
  l.pid,
  a.usename,
  a.query_start,
  l.mode,
  l.granted
from pg_locks l
join pg_catalog.pg_class c ON c.oid = l.relation
join pg_catalog.pg_stat_activity a ON a.procpid = l.pid
where l.pid <> pg_backend_pid()
order by relname;