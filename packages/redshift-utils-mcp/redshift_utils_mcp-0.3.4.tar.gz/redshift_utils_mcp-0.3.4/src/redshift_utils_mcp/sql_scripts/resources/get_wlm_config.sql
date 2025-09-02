-- Purpose: Retrieves the current Workload Management (WLM) configuration details
--          for user-defined service classes (queues).
--          Handles both Manual WLM (classes 6-13) and indicates Auto WLM (classes 100-107).
--          Service classes 1-4 are reserved for system use. Service class 5 is Superuser.
-- Usage: Used by the 'wlm_configuration' resource handler.
-- Parameters: None
-- Note: For Auto WLM, concurrency_slots and memory_mb_per_slot will be -1,
--       indicating dynamic management by Redshift. Configuration is managed
--       via parameters like wlm_json_configuration or console settings.
SELECT
    service_class,
    TRIM(name) AS service_class_name,       -- Use TRIM for cleaner output
    num_query_tasks AS concurrency_slots,   -- Concurrency level (-1 indicates Auto WLM)
    query_working_mem AS memory_mb_per_slot,-- Memory per slot in MB (-1 indicates Auto WLM)
    max_execution_time AS timeout_ms,       -- Timeout in milliseconds (0 means no timeout)
    user_group_wild_card,                   -- Note the underscore
    query_group_wild_card,                  -- Note the underscore
    user_role_wild_card,                    -- Added based on documentation
    concurrency_scaling,                    -- Added based on documentation
    query_priority                          -- Added based on documentation
FROM
    STV_WLM_SERVICE_CLASS_CONFIG
WHERE
    service_class > 5
ORDER BY
    service_class;