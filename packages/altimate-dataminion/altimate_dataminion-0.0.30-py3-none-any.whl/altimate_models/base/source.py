import sys
from contextlib import contextmanager
from typing import Any, Dict, Generator, Optional, Text

from pydantic.v1.main import BaseModel

from altimate_models.constants import DEFAULT_CLIENT_DB_CONNECTION_TIMEOUT

try:
    from sqlalchemy import create_engine
except ImportError:
    pass


class DataSource(BaseModel):
    id: Optional[Text]
    name: Text
    type: Text
    description: Optional[Text]
    connection_info: Optional[Text]
    connection_hash: Optional[Text]
    statement_timeout_in_ms: Optional[int]
    key_pair: Optional[Dict]
    auth_type: Optional[Text]

    @classmethod
    def prompt(cls, data_store_config: Dict):
        raise NotImplementedError()

    def cred_prompt(self):
        raise NotImplementedError()

    @classmethod
    def get_connection_information(cls, data_store_config: Dict):
        raise NotImplementedError()

    def get_databases(self):
        raise NotImplementedError()

    def test_connection(self):
        raise NotImplementedError()

    def get_connection_string(self, *args, **kwargs) -> Text:
        raise NotImplementedError

    def drop_credentials(self):
        raise NotImplementedError

    def get_resource(self):
        raise NotImplementedError

    def get_identifier_and_fqn(self):
        raise NotImplementedError

    @classmethod
    def get_resource_config(cls, resource_config: Dict):
        raise NotImplementedError()

    @classmethod
    def map_config_to_source(cls, config: Dict):
        raise NotImplementedError()

    @classmethod
    def get_config_from_url(cls, connection_info: str):
        raise NotImplementedError()

    def update_credentials(self, key: str):
        raise NotImplementedError()

    def override_schema(self, schema):
        raise NotImplementedError()

    def get_connect_args(self):
        return {"connect_timeout": DEFAULT_CLIENT_DB_CONNECTION_TIMEOUT}

    @contextmanager
    def get_engine(self):
        """
        has to be run as a context manager
        or else the tunnel will close
        """
        if not "sqlalchemy" in sys.modules:
            raise ImportError(
                "sqlalchemy is not installed. Please install sqlalchemy to test connections"
            )
        with self.get_bound_host_and_port() as conn_args:
            # connect_args might not be supported by all dialects
            engine = create_engine(
                self.get_connection_string(**conn_args),
                connect_args=self.get_connect_args(),
            )
            try:
                yield engine
                # the ssh tunnel would close up after the outer context manager exits
            except Exception as e:
                # re-raise the exceptions here so as to not catch them here and silently fail
                raise e
            finally:
                engine.raw_connection().close()
                if engine.dispose:
                    engine.dispose()

    @contextmanager
    def get_bound_host_and_port(self) -> Generator[Dict[str, Any], None, None]:
        # this is where the ssh tunneling would happen
        try:
            args: Dict[str, Any] = {}
            if hasattr(self, "host"):  # type: ignore
                args["host"] = self.host
            if hasattr(self, "port"):  # type: ignore
                args["port"] = self.port
            # we might have more args in the future. add them here
            yield args  # type: ignore
        except Exception as e:
            # re-raise exceptions raised in the context block
            raise e

    def get_dict(self):
        config = self.dict()
        config.pop("connection_hash")
        config.pop("connection_info")
        return config
