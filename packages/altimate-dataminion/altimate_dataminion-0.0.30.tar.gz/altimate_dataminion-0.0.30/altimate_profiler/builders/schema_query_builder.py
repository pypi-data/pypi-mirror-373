from typing import Dict, List

from altimate_models.shared_models import Policy
from altimate_profiler.builders.base_builder import Base
from altimate_profiler.metrics.schema_metric_type import SchemaMetricType


class SchemaQueryBuilder(Base):
    def __init__(
        self,
        policy: Policy,
        discovery_data: dict,
    ):
        self.policy = policy
        self.discovery_data = discovery_data

    def _columns_present(self, params):
        columns = [column.lower() for column in params["columns"]]
        existing_columns = [
            row["COL_NAME"].lower() for row in self.discovery_data["rows"]
        ]
        return all([column in existing_columns for column in columns])

    def _columns_not_present(self, params):
        columns = [column.lower() for column in params["columns"]]
        existing_columns = [
            row["COL_NAME"].lower() for row in self.discovery_data["rows"]
        ]
        return all([(column not in existing_columns) for column in columns])

    def _has_primary_key(self, params):
        raise NotImplementedError("Not Applicable for this source")

    def _has_consistent_fk_names(self, params):
        raise NotImplementedError("Not Applicable for this source")

    def _index_with_pattern(self, params):
        raise NotImplementedError("Not Applicable for this source")

    def _column_data_type(self, params):
        column = params["column"]
        for row in self.discovery_data["rows"]:
            if row["COL_NAME"].lower() == column.lower():
                return row["COL_TYPE"].lower()

    def _is_same_as(self, params):
        raise NotImplementedError("Not Implemented sama as check")

    def compile(self) -> List[Dict]:
        row = {}
        columns = []
        for idx, term in enumerate(self.policy.terms):
            column_name = term.metric + "_" + str(idx)
            columns.append(column_name)
            row[column_name] = getattr(
                self, SchemaMetricType[term.metric.upper()].value
            )(term.params)

        return [{"columns": columns, "rows": [row]}]
