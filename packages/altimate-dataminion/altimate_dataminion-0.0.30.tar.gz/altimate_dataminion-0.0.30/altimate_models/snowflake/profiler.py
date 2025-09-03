from typing import TYPE_CHECKING

from altimate_models.base.extractor import SQLAlchemyExtractor
from altimate_models.base.profiler import SQLAlchemyProfiler
from altimate_models.shared_models import Policy
from altimate_models.snowflake.dialect import SnowflakeSourceDialect

if TYPE_CHECKING:
    from altimate_models.snowflake.source import SnowflakeSource


class SnowflakeProfiler(SQLAlchemyProfiler):
    def __init__(self, data_source: "SnowflakeSource", policy: Policy, use_account_usage: bool = False):
        # FIXME - raise exception if the database in datasource
        # and that in policy is not the same.
        # data_source.database = policy.resource0.resource.database
        super().__init__(
            extractor=SQLAlchemyExtractor(
                connection_str=data_source.get_connection_string(
                    # database=policy.resource0.resource.database,
                    # schema=policy.resource0.resource.db_schema,
                ),
                data_source=data_source,
            ),
            policy=policy,
            dialect=SnowflakeSourceDialect(),
            use_account_usage=use_account_usage,
        )
