from typing import List, Text

from altimate_models.shared_models import Policy, TableResource
from altimate_profiler.builders.column_metrics_query_builder import (
    ColumnMetricsQueryBuilder,
)
from altimate_profiler.builders.table_query_builder import TableQueryBuilder


class SQLAlchemySourceDialect:
    @classmethod
    def _row_count(cls, table, params):
        return "select COALESCE(COUNT(*), 0)  from {table}".format(table=table)

    @classmethod
    def _duplicate_count(cls, table, params):
        return "select COALESCE((SUM(c) - COUNT(c)), 0) as dulicates from (select md5(row_to_json(ROW({columns}))::TEXT),count(*) as c   from {table} group by md5(row_to_json(ROW({columns}))::TEXT) having count(*) > 1) as t".format(
            columns=",".join(params["columns"]), table=table
        )

    @classmethod
    def _numeric_variance(cls):
        return "variance({column})"

    @classmethod
    def _numeric_median(cls):
        raise NotImplementedError("Median is not implemented")

    @classmethod
    def _null_count_table(cls, table, params):
        raise NotImplementedError("null_count has not been implemented")

    @classmethod
    def _numeric_mode(cls):
        raise NotImplementedError("mode has not been implemented")

    @classmethod
    def _percentile(cls):
        raise NotImplementedError("percentile has not been implemented")

    @classmethod
    def _null_count(cls, table, params):
        raise NotImplementedError("null_count has not been implemented")

    @classmethod
    def _like_percentage(cls):
        raise NotImplementedError("like has not been implemented")

    @classmethod
    def _regex_match_percentage(cls):
        raise NotImplementedError("null_count has not been implemented")

    @classmethod
    def create_table_path(cls, resource: TableResource):
        return f"{resource.database}.{resource.db_schema}.{resource.table}"

    @classmethod
    def _percentage_distinct_count(cls, table, params):
        concat_columns = (
            "CONCAT("
            + ",".join(
                [
                    f"coalesce({column}::text, '')"
                    for column in params.get("columns", [])
                ]
            )
            + ")"
        )
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
    def _freshness(cls):
        raise NotImplementedError("freshness has not been implemented")

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
        return "STDDEV(CAST({column} as double))"

    @classmethod
    def _allowed_values(cls):
        raise NotImplementedError("allowed_values has not been implemented")

    @classmethod
    def _dates_in_future_percentage(cls):
        raise NotImplementedError("dates_in_future_percentage has not been implemented")

    @classmethod
    def _cardinality(cls):
        return "COUNT(DISTINCT {column})"

    @classmethod
    def _allowed_values(cls):
        raise NotImplementedError("allowed_values has not been implemented")

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
    def _std_length(cls):
        return "STDDEV(CAST(LENGTH({column}) as double))"

    @classmethod
    def _categories(cls):
        return "ARRAY_AGG(DISTINCT CAST({column} AS varchar))"

    @classmethod
    def _num_categories(cls):
        return "COUNT(DISTINCT CAST({column} AS varchar))"

    @classmethod
    def _conditional_percentage(cls):
        raise NotImplementedError("conditional_percentage has not been implemented")

    @classmethod
    def _conditional_max(cls):
        raise NotImplementedError

    @classmethod
    def _conditional_min(cls):
        raise NotImplementedError

    @classmethod
    def _conditional_mean(cls):
        raise NotImplementedError

    @classmethod
    def _conditional_count(cls):
        raise NotImplementedError

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
        schemas_to_exclude: List[Text] = None,
        use_account_usage: bool = False,
    ):
        raise NotImplementedError

    @classmethod
    def column_metrics_query(cls, discovery_data, policy: Policy) -> List[Text]:
        builder = ColumnMetricsQueryBuilder(cls, discovery_data, policy)
        query = builder.compile()
        return query

    @classmethod
    def table_metrics_query(cls, policy: Policy) -> List[Text]:
        builder = TableQueryBuilder(cls, policy)
        query = builder.compile()
        return query

    @classmethod
    def access_logs_query(cls):
        raise NotImplementedError

    @classmethod
    def copy_and_load_logs_query(cls):
        raise NotImplementedError
