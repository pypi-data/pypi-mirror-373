from typing import List, Text

from altimate_profiler.metrics.table_metric_type import TableMetricType
from altimate_models.shared_models import Policy
from altimate_profiler.builders.base_builder import Base


class S3TableQueryBuilder(Base):
    def __init__(
            self,
            dialect,
            policy: Policy,
    ):
        self.policy = policy
        self.dialect = dialect


    def _gen_sql(self, metric, params, table):
        attr = getattr(self.dialect, metric._value_)
        return attr(table, params)

    def compile(self) -> List[Text]:
        metrics_queries = []
        all_filters = ' AND '.join(x for x in [self.policy.resource0.filters, self.policy.filters] if x)
        table = self.dialect._table_sql(self.policy.resource0.resource.bucket, self.policy.resource0.resource.path, self.policy.resource0.resource.options, all_filters)
        for term in self.policy.terms:
            metrics_queries.append(self._gen_sql(TableMetricType[term.metric.upper()], term.params, table))
        return metrics_queries
