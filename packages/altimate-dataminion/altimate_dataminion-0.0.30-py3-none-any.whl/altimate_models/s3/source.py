import sys
from typing import Dict, Optional, Text

try:
    import boto3
    import click
except ImportError:
    pass

from altimate_models.base.source import DataSource
from altimate_models.shared_models import Resource, ResourceType, S3Resource
from altimate_profiler.exceptions import AltimateDataStoreConnectionException
from altimate_profiler.utils import green_bold_string, red, sha256_encoding


class S3Source(DataSource):
    NAME = "s3"

    aws_access_key_id: Optional[Text]
    aws_secret_access_key: Optional[Text]
    region: Text
    bucket: Text
    prefix: Text
    file_format: Text
    options: Optional[Dict[Text, Text]]

    s3_endpoint: Optional[Text] = None
    s3_use_ssl: Optional[Text] = None
    s3_url_style: Optional[Text] = None

    def get_connection_string(self, *args, **kwargs) -> Text:
        connection_str = """
INSTALL httpfs;
LOAD httpfs;
SET s3_region='{region}';
SET s3_access_key_id='{access_key}';
SET s3_secret_access_key='{secret_key}';
        """

        if self.s3_endpoint:
            connection_str += f"\nSET s3_endpoint='{self.s3_endpoint}';"
        if self.s3_use_ssl:
            connection_str += f"\nSET s3_use_ssl='{self.s3_use_ssl}';"
        if self.s3_url_style:
            connection_str += f"\nSET s3_url_style='{self.s3_url_style}';"

        return connection_str.format(
            region=self.region,
            access_key=self.aws_access_key_id,
            secret_key=self.aws_secret_access_key,
        )

    @classmethod
    def get_connection_information(cls, data_store_config: Dict):
        data_store_config[
            "connection_info"
        ] = f"{data_store_config['bucket']}.{data_store_config['region']}/{data_store_config['prefix']}?file_format={data_store_config['file_format']}"
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
        data_store_config["bucket"] = click.prompt("bucket", type=str)
        data_store_config["aws_access_key_id"] = click.prompt(
            "aws_access_key_id", type=str
        )
        data_store_config["aws_secret_access_key"] = click.prompt(
            "aws_secret_access_key", type=str, hide_input=True
        )
        data_store_config["region"] = click.prompt("region", type=str, default="")
        data_store_config["prefix"] = click.prompt("Path to file", type=str, default="")
        data_store_config["file_format"] = click.prompt(
            "file format", type=click.Choice(["csv", "parquet", "json"])
        )
        data_store_config["options"] = {}
        if data_store_config["file_format"] == "csv":
            data_store_config["options"]["header"] = click.prompt(
                "header", type=bool, default=True
            )
            data_store_config["options"]["delim"] = (
                '"' + click.prompt("delimiter", type=str, default=",") + '"'
            )

        data_store_config = cls.get_connection_information(data_store_config)
        return S3Source(**data_store_config)

    def cred_prompt(self):
        if "click" not in sys.modules:
            raise ImportError(
                "click is not installed. Please install click to connect to S3."
            )
        self.aws_access_key_id = click.prompt("aws_access_key_id", type=str)
        self.aws_secret_access_key = click.prompt(
            "aws_secret_access_key", type=str, hide_input=True
        )
        conn_info = self.get_connection_information(self.__dict__)
        self.connection_info = conn_info["connection_info"]
        self.connection_hash = conn_info["connection_hash"]

    def test_connection(self):
        if "boto3" in sys.modules:
            session = boto3.Session(
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
            )

            # Create a client for S3 service
            s3_client = session.client("s3")

            try:
                # Test the connection by listing objects in the bucket
                response = s3_client.list_objects_v2(Bucket=self.bucket)
                print(green_bold_string("Successfully connected to S3!"))
            except Exception as e:
                print(red("Connection to S3 failed."))
                print("Check your credentials and try again.")
                raise AltimateDataStoreConnectionException(
                    f"Connection to {self.name} failed."
                    f" Please check the credentials"
                )
        else:
            print("boto3 is not installed. Please install boto3 to connect to S3.")

    def drop_credentials(self):
        config_dict = self.dict()
        aws_access_key_id = config_dict.pop("aws_access_key_id")
        aws_secret_access_key = config_dict.pop("aws_secret_access_key")
        return config_dict

    def get_resource(self):
        return Resource(
            resource_type=ResourceType.FILE,
            resource=S3Resource(
                bucket=self.bucket,
                path=self.prefix,
                format=self.file_format,
                options=self.options,
            ),
        )

    @classmethod
    def get_config_from_url(cls, connection_info):
        file_format = ""

        if "?" in connection_info:
            resource_path, params = connection_info.split("?")
            for param in params.split("&"):
                key, value = param.split("=")
                if key == "file_format":
                    file_format = value
        else:
            resource_path = connection_info
        bucket, region = resource_path.split("/")[0].split(".")
        prefix = "/".join(resource_path.split("/")[1:])
        return {
            "bucket": bucket,
            "region": region,
            "prefix": prefix,
            "file_format": file_format,
        }

    def get_identifier_and_fqn(self):
        identifier = (
            f"{self.type}://{self.bucket}/{self.prefix}?file_format={self.file_format}"
        )
        fqn = f"bucket={self.bucket}"
        return identifier, fqn

    @classmethod
    def get_resource_config(cls, resource_config: Dict):
        filters = resource_config.get("filters")
        identifier = resource_config.get("identifier")
        data_store_type, path = identifier.split("://")
        options = resource_config.get("options")
        resource_path, params = path.split("?")
        file_format = params.split("=")[1]
        bucket = resource_path.split("/")[0]
        path = "/".join(resource_path.split("/")[1:])

        resource = S3Resource(
            bucket=bucket,
            path=path,
            format=file_format,
            options=options,
        )

        return Resource(
            resource_type=ResourceType.FILE, resource=resource, filters=filters
        )

    @classmethod
    def map_config_to_source(cls, config: Dict):
        connection_info = config.get("connection_info")
        if not connection_info:
            return config
        s3_config = cls.get_config_from_url(connection_info)
        config["bucket"] = s3_config["bucket"]
        config["region"] = s3_config["region"]
        config["prefix"] = s3_config["prefix"]
        config["file_format"] = config.get("file_format") or s3_config["file_format"]
        config.pop("connection_info")
        return config

    def override_schema(self, schema):
        return schema
