import sys
from typing import Dict, Optional, Text

try:
    import click
    from sqlalchemy import create_engine
except ImportError:
    pass
from urllib.parse import quote_plus

from altimate_models.base.source import DataSource
from altimate_models.base.utils import load_private_key
from altimate_models.shared_models import (
    PrivateKeyType,
    Resource,
    ResourceType,
    TableResource,
)
from altimate_profiler.exceptions import AltimateDataStoreConnectionException
from altimate_profiler.utils import green_bold_string, red, sha256_encoding


class SnowflakeSource(DataSource):
    NAME = "snowflake"
    account: Optional[Text]
    role: Optional[Text]
    warehouse: Optional[Text]
    user: Optional[Text]
    password: Optional[Text]
    database: Optional[Text]
    sync_credentials: bool = False

    def get_connection_string(self, *args, **kwargs) -> Text:
        connection_string = "{NAME}://{user}:{password}@{account}/{database}".format(
            NAME=self.NAME,
            user=self.user,
            password=quote_plus(self.password),
            account=self.account,
            database=self.database,
            warehouse=self.warehouse,
            role=self.role,
        )
        # uncomment this when we add support for changing schema
        # CAUTION: schema is used internally by pydantic.
        # when we do add this, use a different name
        # if schema:
        #     connection_string += "/{schema}".format(schema=schema)
        connection_string += "?warehouse={warehouse}&role={role}".format(
            warehouse=self.warehouse,
            role=self.role,
        )
        return connection_string

    @classmethod
    def get_connection_information(cls, data_store_config: Dict):
        data_store_config[
            "connection_info"
        ] = f"{data_store_config['account']}/{data_store_config['database']}?role={data_store_config['role']}&warehouse={data_store_config['warehouse']}"
        data_store_config["connection_hash"] = sha256_encoding(
            data_store_config["connection_info"]
        )
        return data_store_config

    @classmethod
    def prompt(cls, data_store_config: Dict):
        if "click" not in sys.modules:
            raise ImportError(
                "click is not installed. Please install click to connect to S3."
            )
        data_store_config["account"] = click.prompt("account", type=str)
        data_store_config["role"] = click.prompt(
            "role", type=str, default="ACCOUNTADMIN"
        )
        data_store_config["warehouse"] = click.prompt("warehouse", type=str)
        data_store_config["user"] = click.prompt("user", type=str)
        data_store_config["password"] = click.prompt(
            "password", type=str, hide_input=True
        )
        data_store_config["database"] = click.prompt("database", type=str)
        data_store_config["sync_credentials"] = click.confirm(
            "sync credentials with altimate?", default=False
        )
        data_store_config = cls.get_connection_information(data_store_config)
        return SnowflakeSource(**data_store_config)

    def cred_prompt(self):
        if "click" not in sys.modules:
            raise ImportError(
                "click is not installed. Please install click to connect to S3."
            )
        self.user = click.prompt("user", type=str)
        self.password = click.prompt("password", type=str, hide_input=True)
        self.sync_credentials = click.confirm(
            "sync credentials with altimate?", default=False
        )
        conn_info = self.get_connection_information(self.__dict__)
        self.connection_info = conn_info["connection_info"]
        self.connection_hash = conn_info["connection_hash"]

    def get_databases(self):
        """
        Fetch all available databases from Snowflake using the INFORMATION_SCHEMA.DATABASES view.
        """
        try:
            with self.get_engine() as engine:
                with engine.connect() as connection:
                    # Use the configured warehouse
                    connection.execute(f"USE WAREHOUSE {self.warehouse}")
                    result = connection.execute(
                        """
                            SELECT
                                database_name
                            FROM
                            SNOWFLAKE.ACCOUNT_USAGE.DATABASES
                            WHERE deleted is null
                            AND database_name not in ('SNOWFLAKE', 'SNOWFLAKE_SAMPLE_DATA')
                            AND database_name not like 'USER$%'

                        """
                    )
                    databases = [dict(row) for row in result]
                    return databases
        except Exception as e:
            print("Failed to fetch databases from Snowflake.")
            print("Check your connection and credentials, then try again.")
            raise e

    def test_connection(self):
        if not "sqlalchemy" in sys.modules:
            raise ImportError(
                "sqlalchemy is not installed. Please install sqlalchemy to test connections"
            )
        try:
            with self.get_engine() as engine:
                engine.connect()
                print(green_bold_string("Successfully connected to Snowflake!"))

        except Exception as e:
            print(red(f"Connection to Snowflake failed. Error: {e}"))
            print("Check your credentials and try again.")
            raise AltimateDataStoreConnectionException(
                f"Connection test for user {self.user} failed for account {self.account}."
            )

    def drop_credentials(self):
        config_dict = self.dict()
        password = config_dict.pop("password")
        username = config_dict.pop("user")
        if self.sync_credentials:
            config_dict["key"] = f"altimate:{username}:{password}"
        return config_dict

    def get_resource(self):
        if self.database is None:
            raise ValueError("database must be set to get resource")
        return Resource(
            resource_type=ResourceType.TABLE,
            resource=TableResource(
                database=self.database,
            ),
        )

    def get_identifier(self):
        if "click" not in sys.modules:
            raise ImportError(
                "click is not installed. Please install click to connect to S3."
            )
        schema = click.prompt("schema", str)
        table = click.prompt("table", str)
        identifier = f"{self.NAME}://{self.database}/{schema}/{table}"
        fqn = f"database={self.database}/schema={schema}/table={table}"
        return identifier, fqn

    @classmethod
    def get_resource_config(cls, resource_config: Dict):
        filters = resource_config.get("filters")
        identifier = resource_config.get("identifier")
        if identifier is None:
            raise ValueError("identifier must be set to get resource")
        data_store_type, path = identifier.split("://")
        database, schema, table = path.split(".")
        resource = TableResource(database=database, schema=schema, table=table)
        return Resource(
            resource_type=ResourceType.TABLE, resource=resource, filters=filters
        )

    def get_identifier_and_fqn(self):
        if "click" not in sys.modules:
            raise ImportError(
                "click is not installed. Please install click to connect to S3."
            )
        schema = click.prompt("schema", type=str)
        table = click.prompt("table", type=str)
        identifier = f"{self.NAME}://{self.database}.{schema}.{table}"
        fqn = f"database={self.database}/schema={schema}/table={table}"
        return identifier, fqn

    @classmethod
    def map_config_to_source(cls, config):
        connection_info = config.get("connection_info")
        if not connection_info:
            return config
        snowflake_config = cls.get_config_from_url(connection_info)
        for k, v in snowflake_config.items():
            config[k] = v
        config.pop("connection_info")
        return config

    @classmethod
    def get_config_from_url(cls, connection_info):
        url, params = connection_info.split("?")
        account, database = url.split("/")
        config = {"account": account, "database": database}
        for param in params.split("&"):
            key, value = param.split("=")
            config[key] = value
        return config

    def update_credentials(self, credentials: str):
        _user, _pass = credentials.split(":")
        self.user = _user
        self.password = _pass

    def override_schema(self, schema):
        return schema

    def get_connect_args(self):
        connect_args = super().get_connect_args()
        if self.statement_timeout_in_ms is not None:
            connect_args["session_parameters"] = {
                "STATEMENT_TIMEOUT_IN_SECONDS": self.statement_timeout_in_ms // 1000
            }
        if self.auth_type == "key_pair":
            connect_args["private_key"] = load_private_key(
                self.key_pair["private_key"],
                self.key_pair.get("type", PrivateKeyType.PEM.value),
                self.key_pair.get("passphrase"),
            )
        return connect_args
