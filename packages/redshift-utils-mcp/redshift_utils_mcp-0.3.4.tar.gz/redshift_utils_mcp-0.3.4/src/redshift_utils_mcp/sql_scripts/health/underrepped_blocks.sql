-- Purpose: Counts the number of blocks with fewer than 2 copies (potentially under-replicated).
-- Parameters: None
-- Note: Assumes a standard replication factor of 2 (typical for multi-node clusters).
-- Blocks with num_values < 2 might indicate under-replication.
SELECT COUNT(*) AS underrepped_blocks_count
FROM stv_blocklist
WHERE num_values < 2;