
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from altimate_models.base.source import DataSource
from altimate_models.s3.csv_source_dialect import CsvSourceDialect
from altimate_models.s3.json_source_dialect import JsonSourceDialect
from altimate_models.s3.parquet_source_dialect import ParquetSourceDialect
from altimate_models.duckdb.profiler import DuckDBProfiler
from altimate_models.shared_models import Policy
from altimate_models.s3.extractor import S3Extractor


class S3Profiler(DuckDBProfiler):
    dialects = {
        "csv": CsvSourceDialect,
        "parquet": ParquetSourceDialect,
        "json": JsonSourceDialect,
    }

    def __init__(self, data_source: "DataSource", policy: Policy, use_account_usage: bool = False):
        super().__init__(
            extractor=S3Extractor(
                data_source.get_connection_string()),
            policy=policy,
            dialect=self.dialects[policy.resource0.resource.format](),
            use_account_usage=use_account_usage,
        )


