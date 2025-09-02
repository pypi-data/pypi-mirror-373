-- Purpose: Retrieves detailed execution metrics for each step of a specific query ID from the recommended SYS view.
-- Source: SYS_QUERY_DETAIL (replaces SVL_QUERY_REPORT as per AWS recommendation)
-- Note: Provides step-level metrics. Slice-level detail, workmem, cpu_time, queue_time, and detailed step_state are not directly available in this view.
-- Parameters:
--   :query_id (bigint): The ID of the query.
SELECT
    query_id,
    segment_id,
    step_id,
    step_name,
    table_name, -- Provides table context for scan steps
    is_rrscan, -- Range-restricted scan used?
    (spilled_block_local_disk > 0 OR spilled_block_remote_disk > 0) AS is_diskbased, -- Derived: Indicates spilling to disk (local or S3)
    output_rows AS rows, -- Rows produced by the step
    output_bytes AS bytes, -- Bytes produced by the step
    duration AS run_time, -- Total time for the step (microseconds)
    is_active -- 't' if step is still running, 'f' if completed (doesn't show 'Failed')
FROM sys_query_detail
WHERE query_id = :query_id
  AND metrics_level = 'step' -- Ensure we only get step-level rows
ORDER BY segment_id, step_id; -- Order logically by segment and step