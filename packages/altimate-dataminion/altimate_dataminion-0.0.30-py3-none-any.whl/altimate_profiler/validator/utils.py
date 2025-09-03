"""
This file has code that defines several functions that are used to fetch metadata information, such as the schema and profiler, of a data source.  The schema_mapper and profile_mapper functions are used to convert the data into a format that is expected by a contract definition. The fetch_schema and fetch_profile functions are responsible for loading the configuration and calling the appropriate functions to retrieve the metadata information. Additionally, the code defines several helper functions that are used to get metrics specific to certain column types (e.g. "int", "float", "string", "number") and others for semantic types (e.g. ID, date).
"""
from typing import Dict, List

from altimate_models import DataSource, ProfileConfig
from altimate_models.constants import COLUMN_TO_PERFORMANCE
from altimate_profiler import get_metrics_profile, get_schema_profile
from altimate_profiler.validator.mappers import schema_mapper


def gen_contract_for_performance(profile):
    output = {}
    for column, metric in profile.items():
        for name, value in metric.items():
            output[
                COLUMN_TO_PERFORMANCE[
                    (
                        column,
                        name,
                    )
                ]
            ] = value
    return output


def fetch_schema(
    data_source: DataSource,
    profile_config: ProfileConfig,
    use_account_usage: bool = False,
) -> List[Dict]:
    """
    Function which loads config and gets the schema for the source
    """
    original_schema = get_schema_profile(
        data_source=data_source, profile_config=profile_config, use_account_usage=use_account_usage
    )
    return schema_mapper(original_schema)


def fetch_profile(data_source: DataSource, profile_config: ProfileConfig) -> Dict:
    """
    Function which loads config and gets the Profile for the source
    """
    return {
        "policies": get_metrics_profile(
            data_source=data_source, profile_config=profile_config
        )
    }
