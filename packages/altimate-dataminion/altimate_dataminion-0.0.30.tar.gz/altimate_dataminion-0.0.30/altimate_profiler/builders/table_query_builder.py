from typing import List, Text

from altimate_models.shared_models import Policy, Resource
from altimate_profiler.builders.base_builder import Base
from altimate_profiler.metrics.table_metric_type import TableMetricType


class TableQueryBuilder(Base):
    def __init__(
        self,
        dialect,
        policy: Policy,
    ):
        self.policy = policy
        self.dialect = dialect

    def _table_sql(self, table, filters):
        if filters:
            table += " WHERE " + filters
        return table

    def _gen_sql(self, metric, params, table):
        attr = getattr(self.dialect, metric._value_)
        return attr(table, params)

    def _gen_table_path(self, resource: Resource):
        return "{}.{}.{}".format(
            resource.resource.database,
            resource.resource.db_schema,
            resource.resource.table,
        )

    def compile(self) -> List[Text]:
        metrics_queries = []
        all_filters = " AND ".join(
            x for x in [self.policy.resource0.filters, self.policy.filters] if x
        )
        table = self._table_sql(
            self._gen_table_path(self.policy.resource0), all_filters
        )
        for term in self.policy.terms:
            metrics_queries.append(
                self._gen_sql(TableMetricType[term.metric.upper()], term.params, table)
            )
        return metrics_queries
