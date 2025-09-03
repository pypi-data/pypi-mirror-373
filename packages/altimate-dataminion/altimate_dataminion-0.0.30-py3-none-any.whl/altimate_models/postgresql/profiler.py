from typing import TYPE_CHECKING

from altimate_models.base.profiler import SQLAlchemyProfiler
from altimate_models.postgresql.dialect import PostgreSQLSourceDialect
from altimate_models.postgresql.extractor import PostgreSQLExtractor
from altimate_models.shared_models import Policy, ResourceType

if TYPE_CHECKING:
    from altimate_models.postgresql.source import PostgresSource


class PostgreSQLProfiler(SQLAlchemyProfiler):
    def __init__(self, data_source: "PostgresSource", policy: Policy, use_account_usage: bool = False):
        if policy.resource0.resource_type != ResourceType.TABLE:
            raise Exception("PostgreSQLProfiler only supports table resources")

        # FIXME - There should be a check here to ensure that
        # database in source and in policy both match
        super().__init__(
            extractor=PostgreSQLExtractor(
                connection_str=data_source.get_connection_string(
                    # database=policy.resource0.resource.database,
                    # schema=policy.resource0.resource.db_schema,
                ),
                data_source=data_source,
            ),
            policy=policy,
            dialect=PostgreSQLSourceDialect(),
            use_account_usage=use_account_usage,
        )
