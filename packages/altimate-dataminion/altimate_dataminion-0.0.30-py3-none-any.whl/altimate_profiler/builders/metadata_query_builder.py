from typing import List, Text

from altimate_profiler.builders.base_builder import Base
from altimate_profiler.metrics.metadata_metric_type import MetadataMetricType


class MetadataQueryBuilder(Base):
    def __init__(self, dialect):
        self.dialect = dialect

    def _gen_sql(self, column, metric):
        attr = getattr(self.dialect, metric._value_)
        return f"{attr().format(column=column)} AS {column}__{metric.name}"

    def get_metrics(
        self,
        columns: List[Text],
        resource_name: Text,
        metrics: List[MetadataMetricType],
    ) -> Text:
        queries = []
        for column in columns:
            for metric in metrics:
                queries.append(self._gen_sql(column, metric))
        return f"SELECT {', '.join(queries)} FROM {resource_name}"

    def row_count(self, resource_name: Text) -> Text:
        return f"SELECT COUNT(*) FROM {resource_name}"

    def compile(self) -> List[Text]:
        metrics_queries = []
        for term in self.policy.terms:
            metrics_queries.append(
                self._gen_sql(MetadataMetricType(term.metric), term.params)
            )
