-- Purpose: Retrieves the history of the last 10 completed VACUUM operations for a specific table.
-- Source: SYS_VACUUM_HISTORY view
-- Parameter: :table_id - The OID (Object ID) of the table to inspect.

SELECT
    start_time,
    end_time,
    duration / 1000000.0 AS duration_seconds, -- Duration is in microseconds
    vacuum_type,
    status,
    reclaimed_rows,
    reclaimed_blocks * 1.0 / 1024 AS reclaimed_mb -- Blocks are 1MB
FROM
    SYS_VACUUM_HISTORY
WHERE
    table_id = :table_id
    AND status = 'Complete' -- Only show completed vacuums
ORDER BY
    end_time DESC
LIMIT 10; -- Limit to the 10 most recent completed vacuums