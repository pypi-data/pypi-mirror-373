from typing import List, Text

from altimate_profiler.exceptions import AltimateProfilerException
from altimate_profiler.builders.s3_table_query_builder import S3TableQueryBuilder
from altimate_models.shared_models import Policy, S3Resource
from altimate_profiler.builders.s3_column_metrics_query_builder import S3ColumnMetricsQueryBuilder


class DuckDBSourceDialect:

    @classmethod
    def create_table_path(cls, resource: S3Resource, query_type: Text) -> Text:
        raise NotImplementedError

    @classmethod
    def _row_count(cls, table, params):
        return "select COALESCE(COUNT(*), 0)  from {table}".format(table=table)

    @classmethod
    def _duplicate_count(cls, table, params):
        return (
            "select COALESCE((SUM(c) - COUNT(c)), 0) as dulicates from (select md5(row_to_json(ROW({columns}))::TEXT),count(*) as c   from {table} group by md5(row_to_json(ROW({columns}))::TEXT) having count(*) > 1) as t"
            .format(columns=",".join(params["columns"]), table=table)
        )

    @classmethod
    def _percentage_distinct_count(cls, table, params):
        concat_columns = "CONCAT(" + ",".join([f"coalesce({column}:: text, '')" for column in params.get("columns", [])]) + ")"
        sql = """        
        WITH total_rows AS (
          SELECT COUNT(*) AS total
          FROM {table}
        ),
        distinct_rows AS (
          SELECT COUNT(DISTINCT {concat_columns}) AS num_distinct
          FROM {table}
        )
        SELECT
          ROUND((num_distinct * 100.0) / total, 2) AS percentage_distinct_rows
        FROM total_rows, distinct_rows;

        """
        return sql.format(concat_columns=concat_columns, table=table)


    @classmethod
    def _approx_distinct_count(cls):
        return "COUNT(DISTINCT {column})"

    @classmethod
    def _approx_distinctness(cls):
        return "{} / CAST(COUNT(*) AS NUMERIC)".format(cls._approx_distinct_count())

    @classmethod
    def _freshness(cls, table, params):
        time_unit = params.get("timeUnit", "day")
        column = params.get("column")
        if column is None:
            raise AltimateProfilerException("Column is required for freshness")
        return "select MIN(date_diff('{timeUnit}', {column}:: DATE, current_date)) from {table}".format(timeUnit=time_unit, column=column, table=table)

    @classmethod
    def _numeric_mean(cls):
        return "AVG({column})"

    @classmethod
    def _numeric_min(cls):
        return "MIN({column})"

    @classmethod
    def _numeric_max(cls):
        return "MAX({column})"

    @classmethod
    def _numeric_std(cls):
        return "stddev_pop(CAST({column} as double))"

    @classmethod
    def _mean_length(cls):
        return "AVG(LENGTH({column}))"

    @classmethod
    def _max_length(cls):
        return "MAX(LENGTH({column}))"

    @classmethod
    def _min_length(cls):
        return "MIN(LENGTH({column}))"

    @classmethod
    def _dates_in_future_percentage(cls):
        return "SUM(CASE WHEN {column} > current_date THEN 1 ELSE 0 END) * 100 / COALESCE(COUNT(*), 1)"


    @classmethod
    def _std_length(cls):
        return "STDDEV(CAST(LENGTH({column}) as double))"

    @classmethod
    def _categories(cls):
        return "ARRAY_AGG(DISTINCT CAST({column} AS varchar))"

    @classmethod
    def _allowed_values(cls):
        return "SUM(CASE WHEN {column} NOT IN {values} THEN 1 ELSE 0 END)"

    @classmethod
    def _num_categories(cls):
        return "COUNT(DISTINCT CAST({column} AS varchar))"

    @classmethod
    def _conditional_max(cls):
        return "MAX(CASE WHEN {condition} THEN {column} ELSE NULL END)"

    @classmethod
    def _conditional_min(cls):
        return "MIN(CASE WHEN {condition} THEN {column} ELSE NULL END)"

    @classmethod
    def _conditional_percentage(cls):
        return "SUM(CASE WHEN {condition} THEN 1 ELSE 0 END) * 100 / COALESCE(COUNT(*), 1)"

    @classmethod
    def _conditional_mean(cls):
        return "AVG(CASE WHEN {condition} THEN {column} ELSE NULL END)"

    @classmethod
    def _conditional_count(cls):
        return "SUM(CASE WHEN {condition} THEN 1 ELSE 0 END)"

    @classmethod
    def _null_count_table(cls, table, params):
        condition = " AND ".join(
            [f"{column} IS NULL" for column in params["columns"]]
        )
        return f"SELECT SUM(CASE WHEN {condition} THEN 1 ELSE 0 END) FROM {table}".format(table=table,
                                                                                          condition=condition)

    @classmethod
    def _null_percentage(cls):
        return "SUM(CASE WHEN {column} IS NULL THEN 1 ELSE 0 END) *100 / COALESCE(COUNT(*), 1)"

    @classmethod
    def _null_count(cls):
        return "SUM(CASE WHEN {column} IS NULL THEN 1 ELSE 0 END)"

    @classmethod
    def _cardinality(cls):
        return "COUNT(DISTINCT md5({column}))"

    @classmethod
    def _regex_match_percentage(cls):
        return "SUM(CASE WHEN regexp_full_match({column}, '{pattern}') THEN 1.0 ELSE 0.0 END) * 100 / COALESCE(COUNT(*), 1)"

    @classmethod
    def _like_percentage(cls):
        return "SUM(CASE WHEN {column} like '{pattern}' THEN 1.0 ELSE 0.0 END) * 100 / COALESCE(COUNT(*), 1)"

    @classmethod
    def _numeric_mode(cls):
        return "MODE({column})"

    @classmethod
    def _numeric_variance(cls):
        return "var_pop({column})"

    @classmethod
    def _percentile(cls):
        return "PERCENTILE_CONT({value}) within group (order by {column})"

    @classmethod
    def _numeric_median(cls):
        return "median({column})"

    @classmethod
    def _text_int_rate(cls):
        raise NotImplementedError

    @classmethod
    def _text_number_rate(cls):
        raise NotImplementedError

    @classmethod
    def _text_uuid_rate(cls):
        raise NotImplementedError

    @classmethod
    def text_all_spaces_rate(cls):
        raise NotImplementedError

    @classmethod
    def _text_null_keyword_rate(cls):
        raise NotImplementedError

    @classmethod
    def _zero_rate(cls):
        raise NotImplementedError

    @classmethod
    def _negative_rate(cls):
        raise NotImplementedError

    @classmethod
    def _completeness(cls):
        raise NotImplementedError

    @classmethod
    def schema_tables_query(cls, bucket: Text,  path: Text, options: Text):
        raise NotImplementedError

    @classmethod
    def schema_columns_query(cls, path: Text, options: Text):
        raise NotImplementedError

    @classmethod
    def column_metrics_query(cls,  policy: Policy) -> List[Text]:
        builder = S3ColumnMetricsQueryBuilder(cls,  policy)
        query = builder.compile()
        return query

    @classmethod
    def table_metrics_query(cls, policy: Policy) -> List[Text]:
        builder = S3TableQueryBuilder(cls,  policy)
        query = builder.compile()
        return query

    @classmethod
    def _base_query_sample(cls, select_sql: Text, bucket: Text, file_resource: S3Resource = None, filters: Text = None):
        raise NotImplementedError

    @classmethod
    def access_logs_query(cls):
        raise NotImplementedError

    @classmethod
    def copy_and_load_logs_query(cls):
        raise NotImplementedError
