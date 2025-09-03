import sys
from typing import Dict, Optional, Text

try:
    import click
    from sqlalchemy import create_engine
except ImportError:
    pass

from altimate_models.base.source import DataSource
from altimate_models.shared_models import Resource, ResourceType, TableResource
from altimate_profiler.exceptions import AltimateDataStoreConnectionException
from altimate_profiler.utils import green_bold_string, red, sha256_encoding


class PostgresSource(DataSource):
    NAME = "postgres"
    host: Optional[Text]
    port: Optional[Text]
    user: Optional[Text]
    password: Optional[Text]
    database: Optional[Text]
    sync_credentials: bool = False

    def get_connection_string(self, *args, **kwargs) -> Text:
        host = kwargs.get("host", self.host)
        port = kwargs.get("port", self.port)
        return "postgresql://{user}:{password}@{host}:{port}/{database}".format(
            user=self.user,
            password=self.password,
            host=host,
            port=port,
            database=self.database,
        )

    @classmethod
    def get_connection_information(cls, data_store_config: Dict):
        data_store_config[
            "connection_info"
        ] = f"{data_store_config['host']}:{data_store_config['port']}/{data_store_config['database']}"
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
        data_store_config["host"] = click.prompt("host", type=str)
        data_store_config["port"] = click.prompt("port", type=int)
        data_store_config["user"] = click.prompt("user", type=str)
        data_store_config["password"] = click.prompt(
            "password", type=str, hide_input=True
        )
        data_store_config["database"] = click.prompt("database", type=str)
        data_store_config["sync_credentials"] = click.confirm(
            "sync credentials with altimate?", default=False
        )
        data_store_config = cls.get_connection_information(data_store_config)
        return PostgresSource(**data_store_config)

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

    def test_connection(self):
        if not "sqlalchemy" in sys.modules:
            raise ImportError(
                "sqlalchemy is not installed. Please install sqlalchemy to test connections"
            )
        try:
            with self.get_engine() as engine:
                engine.connect()
                print(green_bold_string("Successfully connected to Postgres!"))

        except Exception as e:
            print(red("Connection to Postgres failed."))
            print("Check your credentials and try again.")
            raise AltimateDataStoreConnectionException(
                f"Connection to {self.name} failed." f" Please check the credentials"
            )

    def drop_credentials(self):
        config_dict = self.dict()
        password = config_dict.pop("password")
        username = config_dict.pop("user")
        if self.sync_credentials:
            config_dict["key"] = f"altimate:{username}:{password}"
        return config_dict

    def get_resource(self):
        return Resource(
            resource_type=ResourceType.TABLE,
            resource=TableResource(
                database=self.database,
            ),
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
    def get_resource_config(cls, resource_config: Dict):
        filters = resource_config.get("filters")
        identifier = resource_config.get("identifier")
        data_store_type, path = identifier.split("://")
        database, schema, table = path.split(".")
        resource = TableResource(database=database, schema=schema, table=table)
        return Resource(
            resource_type=ResourceType.TABLE, resource=resource, filters=filters
        )

    @classmethod
    def map_config_to_source(cls, config: Dict):
        connection_info = config.get("connection_info")
        if not connection_info:
            return config
        postgres_config = cls.get_config_from_url(connection_info)
        config["host"] = postgres_config["host"]
        config["port"] = postgres_config["port"]
        config["database"] = postgres_config["database"]
        config.pop("connection_info")
        return config

    @classmethod
    def get_config_from_url(cls, connection_info):
        url, database = connection_info.split("/")
        host, port = url.split(":")
        return {"host": host, "port": port, "database": database}

    def update_credentials(self, credentials: str):
        _user, _pass = credentials.split(":")
        self.user = _user
        self.password = _pass

    def override_schema(self, schema):
        return schema

    def get_connect_args(self):
        connect_args = super().get_connect_args()
        if self.statement_timeout_in_ms is not None:
            connect_args[
                "options"
            ] = f"-c statement_timeout={self.statement_timeout_in_ms}"
        return connect_args
