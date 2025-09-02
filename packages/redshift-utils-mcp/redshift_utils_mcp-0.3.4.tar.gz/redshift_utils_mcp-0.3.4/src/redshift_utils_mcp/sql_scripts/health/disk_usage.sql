-- Purpose: Calculates the overall percentage of disk space used across the cluster.
-- Parameters: None
SELECT
    SUM(used)::DECIMAL * 100 / SUM(capacity)::DECIMAL AS total_disk_usage_pct -- Corrected calculation based on MB units
FROM stv_partitions;
-- Note: 'used' and 'capacity' columns are in 1MB blocks.
-- Consider adding WHERE clause if needed to exclude specific partitions/nodes if applicable.