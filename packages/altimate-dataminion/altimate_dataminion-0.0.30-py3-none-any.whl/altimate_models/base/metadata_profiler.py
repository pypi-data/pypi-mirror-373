import decimal

from altimate_models.base.extractor import SQLAlchemyExtractor
from altimate_models.base.profiler import SQLAlchemyProfiler
from altimate_models.base.source import DataSource
from altimate_models.shared_models import Policy
from altimate_profiler.builders.metadata_query_builder import MetadataQueryBuilder
from altimate_profiler.builders.utils import infer_type, map_type_to_standard_types
from altimate_profiler.metrics.metadata_metric_type import MetadataMetricType


class SqlAlchemyMetadataProfiler(SQLAlchemyProfiler):
    COMMON_METRICS = [
        MetadataMetricType.CARDINALITY,
        MetadataMetricType.NULL_PERCENTAGE,
    ]

    NUMERIC_METRICS = [
        MetadataMetricType.NUMERIC_MAX,
        MetadataMetricType.NUMERIC_MIN,
        MetadataMetricType.NUMERIC_MEAN,
        MetadataMetricType.NUMERIC_STD,
    ]

    TEXT_METRICS = [MetadataMetricType.MIN_LENGTH, MetadataMetricType.MAX_LENGTH]

    def __init__(
        self,
        data_source: DataSource,
        dialect,
        policy: Policy,
        resource_name: str,
    ):
        self.resource_name = resource_name
        self.metadata_query_builder = MetadataQueryBuilder(dialect)
        super().__init__(
            SQLAlchemyExtractor(data_source.get_connection_string()), policy, dialect
        )

    def get_row_count(self):
        query = self.metadata_query_builder.row_count(self.resource_name)
        metadata = self.extractor.run(query)
        return metadata["rows"][0][metadata["columns"][0]]

    def extract_result(self, result, column_result):
        column_metrics = result["columns"]
        for column_metric in column_metrics:
            column, metric = column_metric.split("__")
            column = column.lower()
            metric = metric.lower()
            for row in result["rows"]:
                if isinstance(row[column_metric], decimal.Decimal):
                    column_result[column][metric] = round(float(row[column_metric]), 2)
                elif isinstance(row[column_metric], float):
                    column_result[column][metric] = round(row[column_metric], 2)
                else:
                    column_result[column][metric] = row[column_metric]
        return column_result

    def get_common_metadata(self, column_result: dict):
        # Get CARDINALITY AND NULL PERCENTAGE
        query = self.metadata_query_builder.get_metrics(
            list(column_result.keys()), self.resource_name, self.COMMON_METRICS
        )
        return self.extract_result(self.extractor.run(query), column_result)

    def get_numeric_metadata(
        self, column_result: dict, column_with_inferred_types: dict
    ):
        numeric_columns = [
            col
            for col, col_type in column_result.items()
            if column_with_inferred_types[col] == "NUMERIC"
        ]
        if len(numeric_columns) == 0:
            return column_result
        query = self.metadata_query_builder.get_metrics(
            numeric_columns, self.resource_name, self.NUMERIC_METRICS
        )
        return self.extract_result(self.extractor.run(query), column_result)

    def text_metadata(self, column_result: dict, column_with_inferred_types: dict):
        text_columns = [
            col
            for col, col_type in column_result.items()
            if column_with_inferred_types[col] == "TEXT"
        ]
        if len(text_columns) == 0:
            return column_result
        query = self.metadata_query_builder.get_metrics(
            text_columns, self.resource_name, self.TEXT_METRICS
        )
        return self.extract_result(self.extractor.run(query), column_result)

    def get_metadata(self):
        discovery_data = self.get_discovery_data()
        column_with_inferred_types = {}
        column_result = {}
        resource_result = {}
        for row in discovery_data["rows"]:
            column_name = row["COL_NAME"].lower()
            column_type = row["COL_TYPE"]
            column_result[column_name] = {}
            common_type = map_type_to_standard_types.get(column_type.upper(), "UNKNOWN")
            column_with_inferred_types[column_name] = infer_type(
                column_name, common_type
            )

        resource_result["row_count"] = self.get_row_count()
        column_result = self.get_common_metadata(column_result)
        column_result = self.get_numeric_metadata(
            column_result, column_with_inferred_types
        )
        column_result = self.text_metadata(column_result, column_with_inferred_types)

        return {
            "columns": column_result,
            "resource": resource_result,
        }

    def get_debugdata(self, debug_sql):
        debug_data = self.get_debug_data(debug_sql)
        return debug_data
