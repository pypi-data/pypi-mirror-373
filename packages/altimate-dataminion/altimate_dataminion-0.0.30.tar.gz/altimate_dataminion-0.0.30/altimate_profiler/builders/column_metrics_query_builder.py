from typing import List, Text

from altimate_models.shared_models import Policy
from altimate_profiler.builders.base_builder import Base
from altimate_profiler.metrics.column_metric_type import ColumnMetricType


class ColumnMetricsQueryBuilder(Base):
    def __init__(self, dialect, discovery_data, policy: Policy):
        self.dialect = dialect
        self.discovery_data = discovery_data
        self.policy = policy

    def _base_query_sample(self, select_sql: Text, filters: Text = None):
        sql = """
            SELECT 
                {select_sql}
            FROM {database}.{schema}.{table}
        """.format(
            select_sql=select_sql,
            table=self.policy.resource0.resource.table,
            schema=self.policy.resource0.resource.db_schema,
            database=self.policy.resource0.resource.database,
        )

        if filters:
            sql += f" WHERE {filters}"

        return sql

    def _extract_col_info(self, column):
        return column["COL_NAME"], column["COL_TYPE"]

    def _transform_col_info_metric(self, col_name, metric, table_name):
        alias = "{}__{}".format(col_name, metric._value_)
        attr = getattr(self.dialect, metric._value_)

        if not attr:
            raise Exception(
                "Unreachable: Metric type is defined that does not resolve to a definition."
            )

        select_unformatted = attr()
        select_no_alias = select_unformatted.format("{}".format(col_name))
        select = "{} AS {}".format(select_no_alias, alias)

        return select

    def _transform_col_info(self, col_name, col_type, table_name):
        terms = list(
            filter(lambda x: x.params.get("column") == col_name, self.policy.terms)
        )

        col_sql = [
            self._transform_col_info_metric(
                col_name, ColumnMetricType[term.metric.upper()], table_name
            )
            for term in terms
        ]
        if len(col_sql) == 0:
            return None

        return ",\n\t".join(col_sql)

    def _col_sql(self, item, select_body):
        table_name = item["NAME"]

        col_name, col_type = self._extract_col_info(item)
        col_sql = self._transform_col_info(col_name, col_type, table_name)

        if table_name not in select_body:
            select_body[table_name] = {"sql": [], "timestamp_fields": []}

        if col_sql is not None:
            select_body[table_name]["sql"].append(col_sql)
        # TODO: Better handling of date / time types is needed
        if col_type == "date" or "timestamp" in col_type:
            select_body[table_name]["timestamp_fields"].append(col_name)

    def _select_sql(self, ddata):
        select_body = {}

        [self._col_sql(item, select_body) for item in ddata]
        for table_name, cols in select_body.items():
            select_body[table_name] = {
                "sql": ",\n".join(cols["sql"]),
                "timestamp_fields": cols["timestamp_fields"],
            }

        return select_body

    def _timestamp_field(self, cols):  # TODO: Improve
        if len(cols["timestamp_fields"]) == 0:
            return None

        return cols["timestamp_fields"][0]

    def _gen_sql(self, metric, params, alias):
        attr = getattr(self.dialect, metric._value_)

        if not attr:
            raise Exception(
                "Unreachable: Metric type is defined that does not resolve to a definition."
            )

        select_unformatted = attr()
        select_no_alias = select_unformatted.format(**params)
        select = "{} AS {}".format(select_no_alias, alias)

        return select

    def compile(self) -> List[Text]:
        metrics_query = []

        for t_idx, term in enumerate(self.policy.terms):
            metrics_query.append(
                self._gen_sql(
                    ColumnMetricType[term.metric.upper()], term.params, f"term_{t_idx}"
                )
            )

        # aggregate different level of filters
        all_filters = " AND ".join(
            x for x in [self.policy.resource0.filters, self.policy.filters] if x
        )

        select_sql = ",\n".join(metrics_query)
        query = self._base_query_sample(select_sql=select_sql, filters=all_filters)

        return [query]
