from typing import List, Text

from altimate_models.shared_models import Policy
from altimate_profiler.metrics.column_metric_type import ColumnMetricType
from altimate_profiler.builders.base_builder import Base


class S3ColumnMetricsQueryBuilder(Base):

    def __init__(
            self,
            dialect,
            policy: Policy
    ):
        self.dialect = dialect
        self.policy = policy

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
                self._gen_sql(ColumnMetricType[term.metric.upper()], term.params, f"term_{t_idx}")
            )

        # aggregate different level of filters
        all_filters = ' AND '.join(x for x in [self.policy.resource0.filters, self.policy.filters] if x)

        select_sql = ",\n".join(metrics_query)
        query = self.dialect._base_query_sample(
            select_sql=select_sql,
            bucket=self.policy.resource0.resource.bucket,
            path=self.policy.resource0.resource.path,
            options=self.policy.resource0.resource.options,
            filters=all_filters
        )

        return [query]
