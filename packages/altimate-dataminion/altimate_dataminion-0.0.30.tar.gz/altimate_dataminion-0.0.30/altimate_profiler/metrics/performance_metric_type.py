from enum import Enum


class PerformanceMetricType(Enum):
    """
    List of supported performance metrics
    """

    MAX_EXECUTION_TIME = "_max_execution_time"
    MIN_BYTES_SPILLED_TO_LOCAL_STORAGE = "_min_bytes_spilled_to_local_storage"
    MAX_CREDITS_CONSUMED_BY_QUERY = "_max_credits_consumed_by_query"
    MAX_CREDITS_CONSUMED_BY_WAREHOUSE = "_max_credits_consumed_by_warehouse"
