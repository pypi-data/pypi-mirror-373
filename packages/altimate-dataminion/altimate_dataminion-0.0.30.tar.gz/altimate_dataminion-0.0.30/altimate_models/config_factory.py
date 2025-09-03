from enum import Enum
from typing import Dict, Optional, Type

import click

from altimate_models.base.source import DataSource
from altimate_models.base.ssh_source import SSHSource
from altimate_models.postgresql.source import PostgresSource
from altimate_models.s3.source import S3Source
from altimate_models.snowflake.source import SnowflakeSource
from altimate_models.tableau.source import TableauSource


class DataStoreType(Enum):
    SNOWFLAKE = "snowflake"
    POSTGRES = "postgres"
    S3 = "s3"
    TABLEAU = "tableau"


class DataStoreConfigFactory:
    CLASSES: dict[DataStoreType, Type[DataSource]] = {
        DataStoreType.SNOWFLAKE: SnowflakeSource,
        DataStoreType.POSTGRES: PostgresSource,
        DataStoreType.S3: S3Source,
        DataStoreType.TABLEAU: TableauSource,
    }

    @classmethod
    def prompt(cls, data_store_config: Dict) -> DataSource:
        data_store = cls.CLASSES[DataStoreType(data_store_config["type"])].prompt(
            data_store_config
        )
        has_jumphost = click.confirm("Do you have a jumphost?", default=False)
        if has_jumphost:
            jumphost = click.prompt("jump_hostname", type=str)
            jumpuser = click.prompt("jump_user", type=str)
            private_key_path = click.prompt("private_key_path", type=str)
            private_key_pass = click.prompt(
                "private_key_password", type=str, hide_input=True
            )
            jump_info = {
                "SSH_PKEY_PATH": private_key_path,
                "SSH_PKEY_PW": private_key_pass,
                "SSH_HOST": jumphost,
                "SSH_USER": jumpuser,
            }
            jump_data_store = SSHSource(jump_info=jump_info, original_ds=data_store)
            # test_data_store.test_connection()
            return jump_data_store

        else:
            return data_store

    @classmethod
    def create(cls, data_store_config: Dict) -> DataSource:
        data_store_config = cls.CLASSES[
            DataStoreType(data_store_config["type"])
        ].map_config_to_source(data_store_config)
        return cls.CLASSES[DataStoreType(data_store_config["type"])](
            **data_store_config
        )

    @classmethod
    def create_from_connection_string(
        cls,
        type: str,
        name: str,
        connection_string: str,
        key: str,
        jump_info: Optional[Dict] = None,
        key_pair: Optional[Dict] = None,
        auth_type: Optional[str] = None,
    ) -> DataSource:
        class_obj: Type[DataSource] = cls.CLASSES[DataStoreType(type)]
        configs = class_obj.get_config_from_url(connection_string)
        configs["name"] = name
        configs["type"] = type
        configs["key_pair"] = key_pair
        configs["auth_type"] = auth_type
        return_obj: DataSource = class_obj(**configs)
        return_obj.update_credentials(key)
        if jump_info:
            return_obj = SSHSource(jump_info=jump_info, original_ds=return_obj)
        return return_obj
