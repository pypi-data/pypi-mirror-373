from dataclasses import dataclass
from typing import Text, List

from altimate_models.duckdb.dialect import DuckDBSourceDialect
from altimate_models.duckdb.extractor import DuckDBExtractor
from altimate_profiler.builders.s3_schema_query_builder import S3SchemaQueryBuilder
from altimate_models.shared_models import Policy
from altimate_profiler.builders.custom_query_builder import CustomQueryBuilder


@dataclass
class DuckDBProfiler:
    extractor: DuckDBExtractor
    policy: Policy
    dialect: DuckDBSourceDialect

    def _columns_schema(self, _) -> Text:
        raise NotImplementedError

    def _tables_schema(self, _) -> Text:
        return self.dialect.schema_tables_query(
            path=self.policy.resource0.resource.path,
            options=self.policy.resource0.resource.options
        )

    def _access_logs(self, _) -> Text:
        return self.dialect.access_logs_query()

    def _copy_and_load_logs(self, _) -> Text:
        return self.dialect.copy_and_load_logs_query()

    def _metrics_query(self) -> List[Text]:
        queries = self.dialect.column_metrics_query(
            self.policy
        )
        return queries

    def _custom_query(self) -> List[Text]:
        custom_metric_builder = CustomQueryBuilder(self.policy)
        return custom_metric_builder.compile()

    def _table_query(self):
        return self.dialect.table_metrics_query(self.policy)

    def _schema_policy(self):
        discovery_data = self.get_discovery_data()
        result = S3SchemaQueryBuilder(self.policy, discovery_data).compile()
        return result

    def _discovery_query(self):
        return self.dialect.schema_tables_query(
            bucket=self.policy.resource0.resource.bucket,
            path=self.policy.resource0.resource.path,
            options=self.policy.resource0.resource.options
        )

    def get_discovery_data(self):
        schema = self.extractor.run(self._discovery_query())
        columns = schema["columns"]
        rows = schema["rows"]
        columns.append("path")
        columns.append("file_format")
        for row in rows:
            row["file_path"] = self.policy.resource0.resource.path
            row["file_format"] = self.policy.resource0.resource.format
            row["bucket"] = self.policy.resource0.resource.bucket
        return schema

    def get_debug_data(self, debug_sql):
        return self.extractor.run(debug_sql)

    def get_metrics_data(self):
        if self.policy.policy_type == "custom_check":
            metrics_sql = self._custom_query()
        elif self.policy.policy_type == "column":
            metrics_sql = self._metrics_query()
        elif self.policy.policy_type == "table":
            metrics_sql = self._table_query()
        elif self.policy.policy_type == "schema":
            # TODO: Make this better
            result = self._schema_policy()
            return result
        else:
            raise Exception("Unknown policy type")

        metrics = []
        for sql in metrics_sql:
            metric = self.extractor.run(sql)
            metrics.append(metric)

        return metrics
