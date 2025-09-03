from typing import List, Text

from altimate_models.shared_models import Policy
from altimate_profiler.builders.base_builder import Base
from altimate_profiler.metrics.performance_metric_type import PerformanceMetricType


class PerformanceQueryBuilder(Base):
    """
    Query builder for performance metrics
    TODO: As of right now, multiple queries are executed. We should be able to do this in one query
    """

    def __init__(self, dialect, policy: Policy):
        self.dialect = dialect
        self.policy = policy

    def _gen_sql(self, metric_name, params) -> Text:
        attr = getattr(self.dialect, PerformanceMetricType[metric_name.upper()].value)
        return attr(params)

    def compile(self) -> List[Text]:
        metrics_queries = []

        for term in self.policy.terms:
            metrics_queries.append(self._gen_sql(term.metric, term.params))

        return metrics_queries
