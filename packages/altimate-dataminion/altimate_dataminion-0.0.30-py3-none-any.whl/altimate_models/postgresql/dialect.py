from typing import List, Text

from altimate_models.base.dialect import SQLAlchemySourceDialect
from altimate_profiler.exceptions import AltimateProfilerException


class PostgreSQLSourceDialect(SQLAlchemySourceDialect):
    TIME_UNIT_TO_SECOND_MAPPING = {
        "second": 1,
        "minute": 60,
        "hour": 3600,
        "day": 86400,
        "week": 604800,
        "month": 2592000,
        "year": 31536000,
    }

    @classmethod
    def _freshness(cls, table, params):
        column = params["column"]
        time_unit = params.get("timeUnit", "day")

        divide_by = cls.TIME_UNIT_TO_SECOND_MAPPING.get(time_unit)

        if not divide_by:
            raise AltimateProfilerException(
                "Invalid timeUnit. It must be one of {}".format(
                    ", ".join(cls.TIME_UNIT_TO_SECOND_MAPPING.keys())
                )
            )

        return (
            "SELECT MIN(EXTRACT(EPOCH FROM (NOW() - {column}))) "
            "/ {divide_by} AS freshness FROM {table}".format(
                column=column, divide_by=divide_by, table=table
            )
        )

    @classmethod
    def _numeric_std(cls):
        return "STDDEV(CAST({column} as double precision))"

    @classmethod
    def _text_int_rate(cls):
        return (
            "SUM(CASE WHEN CAST({column} AS varchar) ~ '^([-+]?[0-9]+)$' THEN 1 ELSE 0 END) /"
            " COALESCE(COUNT(*), 1)"
        )

    @classmethod
    def _null_percentage(cls):
        return "SUM(CASE WHEN {column} IS NULL THEN 1 ELSE 0 END) * 100/COALESCE(COUNT(*), 1)"

    @classmethod
    def _text_number_rate(cls):
        return (
            "SUM(CASE WHEN CAST({column} AS varchar) ~"
            " '^([-+]?[0-9]*[.]?[0-9]+([eE][-+]?[0-9]+)?)$' THEN 1 ELSE 0 END) /"
            " COALESCE(COUNT(*), 1)"
        )

    @classmethod
    def _text_uuid_rate(cls):
        return (
            "SUM(CASE WHEN CAST({column} AS varchar) ~"
            " '^([0-9a-fA-F]{{8}}-[0-9a-fA-F]{{4}}-[0-9a-fA-F]{{4}}-[0-9a-fA-F]{{4}}-[0-9a-fA-F]{{12}})$'"
            " THEN 1 ELSE 0 END) / COALESCE(COUNT(*), 1)"
        )

    @classmethod
    def _invalid_email_rate(cls):
        return (
            "SUM(CASE WHEN CAST({column} AS varchar) ~"
            " '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+.[a-zA-Z0-9\\\-.]+$'"
            " THEN 0 ELSE 1 END) / COALESCE(COUNT(*), 1)"
        )

    @classmethod
    def _allowed_values(cls):
        return "SUM(CASE WHEN {column} NOT IN {values} THEN 1 ELSE 0 END)"

    @classmethod
    def _text_all_spaces_rate(cls):
        return (
            "SUM(CASE WHEN CAST({column} AS varchar) ~ '^(\\\\s+)$' THEN 1 ELSE 0 END) /"
            " COALESCE(COUNT(*), 1)"
        )

    @classmethod
    def _text_null_keyword_rate(cls):
        return (
            "SUM(CASE WHEN UPPER(CAST({column} as varchar)) IN ('NULL', 'NONE', 'NIL',"
            " 'NOTHING') THEN 1 ELSE 0 END) / COALESCE(COUNT(*), 1)"
        )

    @classmethod
    def _zero_rate(cls):  # TODO: ?
        return (
            "SUM(CASE WHEN UPPER(CAST({column} as varchar)) IN ('NULL', 'NONE', 'NIL',"
            " 'NOTHING') THEN 1 ELSE 0 END) / COALESCE(COUNT(*), 1)"
        )

    @classmethod
    def _negative_rate(cls):
        return "SUM(CASE WHEN {column} < 0 THEN 1 ELSE 0 END) / COALESCE(COUNT(*), 1)"

    @classmethod
    def _completeness(cls):
        return "COUNT({column}) / COALESCE(COUNT(*), 1)"

    @classmethod
    def _dates_in_future_percentage(cls):
        return (
            "SUM(CASE WHEN {column} > CURRENT_TIMESTAMP THEN 1 ELSE 0 END) * 100"
            " / COALESCE(COUNT(*), 1) "
        )

    @classmethod
    def _conditional_max(cls):
        return "MAX(CASE WHEN {condition} THEN {column} ELSE NULL END)"

    @classmethod
    def _conditional_min(cls):
        return "MIN(CASE WHEN {condition} THEN {column} ELSE NULL END)"

    @classmethod
    def _conditional_count(cls):
        return "SUM(CASE WHEN {condition} THEN 1 ELSE 0 END)"

    @classmethod
    def _conditional_percentage(cls):
        return (
            "SUM(CASE WHEN {condition} THEN 1 ELSE 0 END) * 100 / COALESCE(COUNT(*), 1)"
        )

    @classmethod
    def _conditional_mean(cls):
        return "AVG(CASE WHEN {condition} THEN {column} ELSE 0 END)"

    @classmethod
    def _null_count(cls):
        return "SUM(CASE WHEN {column} IS NULL THEN 1 ELSE 0 END)"

    @classmethod
    def _regex_match_percentage(cls):
        return "SUM(CASE WHEN {column}::TEXT ~ '{pattern}' THEN 1.0 ELSE 0.0 END) * 100 /  COALESCE(COUNT(*), 1) "

    @classmethod
    def _like_percentage(cls):
        return "SUM(CASE WHEN {column}:: TEXT  LIKE '{pattern}' THEN 1.0 ELSE 0.0 END) * 100 / COALESCE(COUNT(*), 1)"

    @classmethod
    def _numeric_mode(cls):
        return "MODE() WITHIN GROUP (ORDER BY {column})"

    @classmethod
    def _percentile(cls):
        return "PERCENTILE_CONT({value}) WITHIN GROUP (ORDER BY {column})"

    @classmethod
    def _numeric_median(cls):
        return "PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY {column})"

    @classmethod
    def _null_count_table(cls, table, params):
        condition = " AND ".join([f"{column} IS NULL" for column in params["columns"]])
        return (
            f"SELECT SUM(CASE WHEN {condition} THEN 1 ELSE 0 END) FROM {table}".format(
                table=table, condition=condition
            )
        )

    @classmethod
    def schema_tables_query(
        cls,
        database_name: Text,
        schema_name: Text,
        table_name: Text = None,
        filters: Text = None,
    ):
        raise NotImplementedError

    @classmethod
    def schema_columns_query(
        cls,
        database_name: Text,
        schema_name: Text,
        table_name: Text = None,
        filters: Text = None,
        schemas_to_exclude: List[Text] = ["information_schema", "pg_catalog"],
    ):
        sql = """
            SELECT lower(c.table_name) AS "NAME",
                lower(c.column_name) AS "COL_NAME",
                lower(c.data_type) AS "COL_TYPE",
                c.ordinal_position AS "COL_SORT_ORDER",
                lower(c.table_catalog) AS "DATABASE",
                lower(c.table_schema) AS "SCHEMA",
                CASE
                    lower(t.table_type)
                    WHEN 'view' THEN 'true'
                    ELSE 'false'
                END "IS_VIEW"
            FROM INFORMATION_SCHEMA.COLUMNS AS c
                LEFT JOIN INFORMATION_SCHEMA.TABLES t ON c.TABLE_NAME = t.TABLE_NAME
                AND c.TABLE_SCHEMA = t.TABLE_SCHEMA
            WHERE LOWER(c.table_catalog) = LOWER('{database_name}')
        """.format(
            database_name=database_name
        )
        excluded_schemas_string = ", ".join([f"'{s}'" for s in schemas_to_exclude])
        if table_name:
            sql += f" AND LOWER(c.table_name)=LOWER('{table_name}')"

        if schema_name:
            sql += f" AND LOWER(c.table_schema)=LOWER('{schema_name}')"
        else:
            sql += f" AND LOWER(c.table_schema) NOT IN ({excluded_schemas_string})"

        if filters:
            sql += f" AND {filters}"

        return sql

    @classmethod
    def query_access_logs_query(cls):
        raise NotImplementedError

    @classmethod
    def query_copy_logs_query(cls):
        raise NotImplementedError
