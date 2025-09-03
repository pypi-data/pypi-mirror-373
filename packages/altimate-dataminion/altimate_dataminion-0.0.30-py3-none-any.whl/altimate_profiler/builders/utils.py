from typing import Text

map_type_to_standard_types = {
    "BOOLEAN": "BOOLEAN",
    "ENUM": "ENUM",
    "NUMERIC": "NUMERIC",
    "VARCHAR": "TEXT",
    "DOUBLE": "NUMERIC",
    "TEXT": "TEXT",
    "DATE": "DATE",
    "TIMESTAMP": "TIMESTAMP",
    "TIME": "TIMESTAMP",
    "INTERVAL": "INTERVAL",
    "BLOB": "TEXT",
    "BITSTRING": "TEXT",
    "FLOAT": "NUMERIC",
    "NUMBER": "NUMERIC",
    "LIST": "LIST",
    "STRUCT": "STRUCT",
    "MAP": "MAP",
    "BIGINT": "INTEGER",
    "CHARACTER VARYING": "TEXT",
    "DOUBLE PRECISION": "NUMERIC",
    "INTEGER": "INTEGER",
}


def infer_type(column_name: Text, column_type: Text):
    # Check if column is an id
    if column_type in ["NUMERIC", "TEXT"]:
        if "id" in column_name.lower():
            return "ID"

    # Check if column is a timestamp
    if column_type in ["TIMESTAMP", "DATE"]:
        return "DATE"
    elif column_type == "TEXT":
        if "date" in column_name.lower():
            return "DATE"

    return column_type
