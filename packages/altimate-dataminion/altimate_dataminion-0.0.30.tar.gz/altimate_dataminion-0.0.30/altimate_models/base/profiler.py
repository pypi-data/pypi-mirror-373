from dataclasses import dataclass
from typing import List, Text

from altimate_models.base.dialect import SQLAlchemySourceDialect
from altimate_models.base.extractor import SQLAlchemyExtractor
from altimate_models.shared_models import Policy
from altimate_models.snowflake.dialect import SnowflakeSourceDialect
from altimate_profiler.builders.custom_query_builder import CustomQueryBuilder
from altimate_profiler.builders.performance_query_builder import PerformanceQueryBuilder
from altimate_profiler.builders.schema_query_builder import SchemaQueryBuilder


@dataclass
class SQLAlchemyProfiler:
    extractor: SQLAlchemyExtractor
    policy: Policy
    dialect: SQLAlchemySourceDialect
    use_account_usage: bool = False

    def _columns_schema(self, _) -> Text:
        return self.dialect.schema_columns_query(
            database_name=self.policy.resource0.resource.database,
            schema_name=self.policy.resource0.resource.db_schema,
            table_name=self.policy.resource0.resource.table,
            filters=self.policy.resource0.resource.filters,
        )

    def _tables_schema(self, _) -> Text:
        return self.dialect.schema_tables_query(
            database_name=self.policy.resource0.resource.database,
            schema_name=self.policy.resource0.resource.db_schema,
            table_name=self.policy.resource0.resource.table,
            filters=self.policy.resource0.resource.filters,
        )

    def _access_logs(self, _) -> Text:
        return self.dialect.access_logs_query()

    def _copy_and_load_logs(self, _) -> Text:
        return self.dialect.copy_and_load_logs_query()

    def _discovery_query(self) -> Text:
        sql = self.dialect.schema_columns_query(
            database_name=self.policy.resource0.resource.database,
            schema_name=self.policy.resource0.resource.db_schema,
            table_name=self.policy.resource0.resource.table,
            use_account_usage=self.use_account_usage,
        )
        return sql

    def _metrics_query(self, discovery_data) -> List[Text]:
        queries = self.dialect.column_metrics_query(discovery_data, self.policy)

        return queries

    def _custom_query(self) -> List[Text]:
        custom_metric_builder = CustomQueryBuilder(self.policy)
        return custom_metric_builder.compile()

    def get_discovery_data(self):
        return self.extractor.run(self._discovery_query())

    def get_debug_data(self, debug_sql):
        return self.extractor.run(debug_sql)

    def _table_query(self):
        return self.dialect.table_metrics_query(self.policy)

    def _performance_query(self):
        if type(self.dialect) != SnowflakeSourceDialect:
            raise Exception("Performance check is only supported for Snowflake")
        performance_query_builder = PerformanceQueryBuilder(self.dialect, self.policy)
        return performance_query_builder.compile()

    def _schema_policy(self):
        discovery_data = self.get_discovery_data()
        result = SchemaQueryBuilder(self.policy, discovery_data).compile()
        return result

    def get_metrics_data(self):
        # TODO: Create Policy Type Abstract Class
        discovery_data = self.get_discovery_data()
        if self.policy.policy_type == "custom_check":
            metrics_sql = self._custom_query()
        elif self.policy.policy_type == "column":
            metrics_sql = self._metrics_query(discovery_data)
        elif self.policy.policy_type == "table":
            metrics_sql = self._table_query()
        elif self.policy.policy_type == "performance":
            metrics_sql = self._performance_query()
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

    def get_table_metadata(self):
        return self.get_metadata(self._tables_schema)

    def get_metadata(self, schema):
        table_metadata = self.extractor.run(self._tables_schema(schema))
        for column_name, column_type in table_metadata.items():
            column_metadata = self.extractor.run(self._columns_schema(column_name))
            table_metadata[column_name] = {
                "type": column_type,
                "metadata": column_metadata,
            }
