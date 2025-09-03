from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from altimate_models.base.source import DataSource

from altimate_models.shared_models import Policy, ProfileConfig, Resource, ResourceType
from altimate_profiler.factory import (
    DialectFactory,
    MetadataFactory,
    ProfilerFactory,
    SchemaTransformerFactory,
)
from altimate_profiler.transformer.metrics import MetricTransformer


def get_schema_profile(
    data_source: "DataSource", profile_config: ProfileConfig, use_account_usage: bool = False
) -> List:
    schemas = []
    for policy in profile_config.policies:
        profiler = ProfilerFactory.create(data_source, policy, use_account_usage)
        discovered_data = profiler.get_discovery_data()
        transformer = SchemaTransformerFactory.create(data_source.type)
        schema = transformer.transform(discovered_data)
        schemas.append(schema)

    return schemas


def get_metrics_profile(
    data_source: "DataSource", profile_config: ProfileConfig, use_account_usage: bool = False
) -> List:
    metrics = []
    for policy in profile_config.policies:
        profiler = ProfilerFactory.create(data_source, policy, use_account_usage)

        raw_metrics = profiler.get_metrics_data()
        transformer = MetricTransformer()

        transformed_metrics = transformer.transform(raw_metrics)

        metrics.append(transformed_metrics)

    return metrics


def get_metadata(data_source: "DataSource", resource: Resource) -> List:
    dialect = DialectFactory.create(data_source)
    if resource.resource_type == ResourceType.FILE:
        resource.resource.options = dialect.get_options(resource.resource.options)
        resource_name = dialect.create_table_path(resource.resource, dialect.DATA_QUERY)
    else:
        resource_name = dialect.create_table_path(resource.resource)

    if resource.filters:
        resource_name = f"{resource_name} WHERE {resource.filters}"

    policy = Policy(
        policy_index=0, resources=[resource], terms=[], policy_type="metadata"
    )
    profiler = MetadataFactory.create(data_source, policy, resource_name)
    return profiler.get_metadata()


def get_debug_data(data_source: "DataSource", debug_sql: str) -> List:
    policy = Policy(policy_index=0, resources=[], terms=[], policy_type="metadata")
    profiler = MetadataFactory.create(data_source, policy, "")
    return profiler.get_debugdata(debug_sql)
