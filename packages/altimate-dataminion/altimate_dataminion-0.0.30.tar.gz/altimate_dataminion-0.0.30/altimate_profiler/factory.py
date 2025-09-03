from typing import Text

from altimate_models.base.extractor import SQLAlchemyExtractor
from altimate_models.base.metadata_profiler import SqlAlchemyMetadataProfiler
from altimate_models.base.source import DataSource
from altimate_models.postgresql.dialect import PostgreSQLSourceDialect
from altimate_models.postgresql.extractor import PostgreSQLExtractor
from altimate_models.postgresql.profiler import PostgreSQLProfiler
from altimate_models.s3.source import S3Source

from altimate_models.duckdb.extractor import DuckDBExtractor
from altimate_models.s3.csv_source_dialect import CsvSourceDialect
from altimate_models.s3.json_source_dialect import JsonSourceDialect
from altimate_models.s3.parquet_source_dialect import ParquetSourceDialect
from altimate_models.duckdb.metadata_profiler import DuckDBMetadataProfiler
from altimate_models.s3.profiler import S3Profiler
from altimate_models.tableau.extractor import TableauExtractor
from altimate_profiler.transformer.duckdb_schema import DuckDBSchemaTransformer
from altimate_models.shared_models import Policy
from altimate_models.snowflake.dialect import SnowflakeSourceDialect
from altimate_models.snowflake.profiler import SnowflakeProfiler

from altimate_profiler.exceptions import AltimateDataStoreNotSupported
from altimate_profiler.transformer.base import Transformer
from altimate_profiler.transformer.schema import SchemaTransformer


class SchemaTransformerFactory:
    SOURCE_MAP = {
        "snowflake": SchemaTransformer,
        "postgres": SchemaTransformer,
        "s3": DuckDBSchemaTransformer,
    }
    TABLE_SOURCES = ["snowflake", "postgres"]
    FILE_SOURCES = ["s3"]

    @classmethod
    def create(cls, data_source_type: Text) -> Transformer:
        transformer = cls.SOURCE_MAP.get(data_source_type)
        if transformer is None:
            raise AltimateDataStoreNotSupported("Invalid data store type")
        return transformer


class MetadataFactory:
    DATA_SOURCE_TO_PROFILER = {
        "snowflake": SqlAlchemyMetadataProfiler,
        "postgres": SqlAlchemyMetadataProfiler,
        "s3": DuckDBMetadataProfiler,
    }

    @classmethod
    def create(
        cls,
        data_source: DataSource,
        policy: Policy,
        resource_name: Text,
    ):
        profiler = cls.DATA_SOURCE_TO_PROFILER.get(data_source.type)
        dialect = DialectFactory.create(data_source)
        if not profiler:
            raise AltimateDataStoreNotSupported("Data source is not supported!")

        return profiler(data_source, dialect, policy, resource_name)


class ProfilerFactory:
    DATA_SOURCE_TO_PROFILER = {
        "snowflake": SnowflakeProfiler,
        "postgres": PostgreSQLProfiler,
        "s3": S3Profiler,
    }

    @classmethod
    def create(cls, data_source: DataSource, policy: Policy, use_account_usage: bool = False):
        profiler = cls.DATA_SOURCE_TO_PROFILER.get(data_source.type)
        if not profiler:
            raise AltimateDataStoreNotSupported("Data source is not supported!")

        return profiler(data_source, policy, use_account_usage)


class DialectFactory:
    DATA_SOURCE_TO_DIALECT = {
        "snowflake": SnowflakeSourceDialect,
        "postgres": PostgreSQLSourceDialect,
        "s3": {
            "csv": CsvSourceDialect,
            "parquet": ParquetSourceDialect,
            "json": JsonSourceDialect,
        }
    }

    @classmethod
    def create(cls, data_source: DataSource):
        if isinstance(
            data_source, S3Source
        ):  # use stronger match than string comparison `data_source.type == "s3":`
            dialect = cls.DATA_SOURCE_TO_DIALECT.get('s3').get(
                data_source.file_format
            )
        else:
            dialect = cls.DATA_SOURCE_TO_DIALECT.get(data_source.type)

        if not dialect:
            raise AltimateDataStoreNotSupported("Data source is not supported!")
        return dialect


class ExtractorFactory:
    DATA_SOURCE_TO_Extractor = {
        "snowflake": SQLAlchemyExtractor,
        "postgres": PostgreSQLExtractor,
        "s3": DuckDBExtractor,
        "tableau": TableauExtractor,
    }

    @classmethod
    def create(cls, data_source: DataSource):
        extractor = cls.DATA_SOURCE_TO_Extractor.get(data_source.type)
        if not extractor:
            raise AltimateDataStoreNotSupported("Data source is not supported!")
        return extractor
