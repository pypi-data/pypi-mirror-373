-- Purpose: Profiles query types (SELECT, INSERT, UPDATE, DELETE, COPY, etc.) by hour over the last 7 days.
--          Calculates total count and duration for each type per hour.
-- Parameters: None (uses fixed 7-day lookback)

WITH profile AS (SELECT database,
                        CASE
                            WHEN "userid" = 1 THEN 'SYSTEM'
                            WHEN REGEXP_INSTR("querytxt", '(padb_|pg_internal)') THEN 'SYSTEM'
                            WHEN REGEXP_INSTR("querytxt", '[uU][nN][dD][oO][iI][nN][gG] ') THEN 'ROLLBACK'
                            WHEN REGEXP_INSTR("querytxt", '[cC][uU][rR][sS][oO][rR] ') THEN 'CURSOR'
                            WHEN REGEXP_INSTR("querytxt", '[fF][eE][tT][cC][hH] ') THEN 'CURSOR'
                            WHEN REGEXP_INSTR("querytxt", '[dD][eE][lL][eE][tT][eE] ') THEN 'DELETE'
                            WHEN REGEXP_INSTR("querytxt", '[cC][oO][pP][yY] ') THEN 'COPY'
                            WHEN REGEXP_INSTR("querytxt", '[uU][pP][dD][aA][tT][eE] ') THEN 'UPDATE'
                            WHEN REGEXP_INSTR("querytxt", '[iI][nN][sS][eE][rR][tT] ') THEN 'INSERT'
                            WHEN REGEXP_INSTR("querytxt", '[vV][aA][cC][uU][uU][mM][ :]') THEN 'VACUUM'
                            WHEN REGEXP_INSTR("querytxt", '[sS][eE][lL][eE][cC][tT] ') THEN 'SELECT'
                            ELSE 'OTHER' END                                                      query_type,
                        DATEPART(hour, starttime)                                                 query_hour_of_day,
                        ROUND(SUM(DATEDIFF(milliseconds, starttime, endtime))::NUMERIC / 1000, 1) query_duration,
                        COUNT(*)                                                                  query_total
                 FROM stl_query
                 WHERE endtime >= DATEADD(day, -7, CURRENT_DATE)
                 GROUP BY 1, 2, 3)
SELECT 
       query_hour_of_day,
       MAX(CASE WHEN query_type = 'SELECT' THEN query_total ELSE NULL END)    AS "select_count",
       MAX(CASE WHEN query_type = 'SELECT' THEN query_duration ELSE NULL END) AS "select_duration",
       MAX(CASE WHEN query_type = 'CURSOR' THEN query_total ELSE NULL END)    AS "cursor_count",
       MAX(CASE WHEN query_type = 'CURSOR' THEN query_duration ELSE NULL END) AS "cursor_duration",
       MAX(CASE WHEN query_type = 'COPY' THEN query_total ELSE NULL END)      AS "copy_count",
       MAX(CASE WHEN query_type = 'COPY' THEN query_duration ELSE NULL END)   AS "copy_duration",
       MAX(CASE WHEN query_type = 'INSERT' THEN query_total ELSE NULL END)    AS "insert_count",
       MAX(CASE WHEN query_type = 'INSERT' THEN query_duration ELSE NULL END) AS "insert_duration",
       MAX(CASE WHEN query_type = 'UPDATE' THEN query_total ELSE NULL END)    AS "update_count",
       MAX(CASE WHEN query_type = 'UPDATE' THEN query_duration ELSE NULL END) AS "update_duration",
       MAX(CASE WHEN query_type = 'DELETE' THEN query_total ELSE NULL END)    AS "delete_count",
       MAX(CASE WHEN query_type = 'DELETE' THEN query_duration ELSE NULL END) AS "delete_duration",
       MAX(CASE WHEN query_type = 'VACUUM' THEN query_total ELSE NULL END)    AS "vacuum_count",
       MAX(CASE WHEN query_type = 'VACUUM' THEN query_duration ELSE NULL END) AS "vacuum_duration"
FROM profile
GROUP BY 1
ORDER BY 1;