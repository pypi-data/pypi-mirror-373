from enum import Enum


class SchemaMetricType(Enum):
    COLUMNS_PRESENT = "_columns_present"
    COLUMNS_NOT_PRESENT = "_columns_not_present"
    HAS_PRIMARY_KEY = "_has_primary_key"
    HAS_CONSISTENT_FK_NAMES = "_has_consistent_fk_names"
    INDEX_WITH_PATTERN = "_index_with_pattern"
    COLUMN_DATA_TYPE = "_column_data_type"
    IS_SAME_AS = "_is_same_as"
