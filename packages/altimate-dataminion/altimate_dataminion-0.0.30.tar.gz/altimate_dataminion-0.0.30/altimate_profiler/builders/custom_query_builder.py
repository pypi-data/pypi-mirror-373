from typing import List, Text

from altimate_models.shared_models import Policy
from altimate_profiler.builders.base_builder import Base


class CustomQueryBuilder(Base):
    def __init__(self, policy: Policy):
        self.policy = policy

    def compile(self) -> List[Text]:
        metrics_queries = []
        for term in self.policy.terms:
            # TODO: Add support for other metrics. Create a Dialect
            if term.params.get("sql"):
                metrics_queries.append(term.params.get("sql"))

        return metrics_queries
