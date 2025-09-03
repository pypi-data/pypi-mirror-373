from enum import Enum


class MetadataMetricType(Enum):
    """
    List of supported performance metrics
    """

    CARDINALITY = "_cardinality"
    NULL_PERCENTAGE = "_null_percentage"
    MAX_LENGTH = "_max_length"
    MIN_LENGTH = "_min_length"
    NUMERIC_MAX = "_numeric_max"
    NUMERIC_MIN = "_numeric_min"
    NUMERIC_MEAN = "_numeric_mean"
    NUMERIC_STD = "_numeric_std"
