from enum import Enum


class TableMetricType(Enum):
    ROW_COUNT = "_row_count"
    DUPLICATE_COUNT = "_duplicate_count"
    NULL_COUNT_TABLE = "_null_count_table"
    PERCENTAGE_DISTINCT_COUNT = "_percentage_distinct_count"
    FRESHNESS = "_freshness"
