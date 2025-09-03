import types
from contextlib import contextmanager
from typing import Any, Dict, Generator, List, Optional, Text, Type

import sshtunnel

from altimate_models.base.source import DataSource
from altimate_models.constants import TEST_SQL_QUERY
from altimate_profiler.exceptions import AltimateDataStoreConnectionException
from altimate_profiler.utils import green_bold_string, red

# SUPPORTED_DATASOURCE_TYPES = Type[PostgresSource]


class SSHSource(DataSource):
    # this class should only be initialized if we have a jump host to worry about
    # if we don't have a jump host, then we should just use the original datasource
    # which is why this is not an Optional field
    jump_info: dict
    # in general, this should be one of the implementations
    # of the abstract class DataSource. currently only supports
    # postgres. However, since sshsource gets initialized in a factory
    # with abstract datastore type so we have to type it as such or else
    # pydantic shouts at us
    original_ds: DataSource
    available_delegated_methods: Optional[List] = None
    available_delegated_props: Optional[List] = None

    def __init__(self, **data):
        # A lot seems to depend on name and type.
        # changing these seems to break stuff so keeping them the same.
        # Ideally, we should have a prefix when using the delegated datasource.
        # maybe a future TODO.
        data["type"] = data[
            "original_ds"
        ].type  # "ssh::{}".format(data["original_ds"].type)
        data["name"] = data[
            "original_ds"
        ].name  # "ssh::{}".format(data["original_ds"].name)
        super().__init__(**data)

        # populate delegated method list
        # only allow delegation to public methods
        # special case made for properties because we are
        # also delegating all that to original ds
        self.available_delegated_methods = [
            f
            for f in dir(self.original_ds)
            if (
                not f.startswith("_")
                and isinstance(getattr(self.original_ds, f), types.MethodType)
            )
        ]
        self.available_delegated_props = [
            f
            for f in dir(self.original_ds)
            if (not f.startswith("_") and f not in self.available_delegated_methods)
        ]

    # DO NOT REMOVE: we go through __getattr__ only if methods do not exist in this or parent class.
    # but because we want sshsource to also mimick a datastore, we need to explicitly override these
    # delegated method to make sure they works.
    def get_connection_string(self, *args, **kwargs) -> Text:
        return self.original_ds.get_connection_string(*args, **kwargs)

    def get_resource(self):
        return self.original_ds.get_resource()

    def get_resource_config(self, resource_config: Dict):
        return self.original_ds.get_resource_config(resource_config)

    def test_connection(self):
        # need to redo all public facing endpoints it seems
        # return self.original_ds.test_connection()
        try:
            with self.get_engine() as engine:
                with engine.connect() as connection:
                    connection.execute(TEST_SQL_QUERY)
                print(
                    green_bold_string(
                        f"Successfully connected to {self.original_ds.name} via jumphost!"
                    )
                )

        except Exception as e:
            print(red("Connection via jump host failed."))
            print("Check your credentials and try again.")
            raise AltimateDataStoreConnectionException(
                f"Connection to {self.original_ds.name} failed."
                f" Please check the credentials"
            )

    # overriding the drop_credentials method to avoid dropping the jump_info
    # thats not held in the original ds
    def drop_credentials(self):
        conf_dict = self.original_ds.drop_credentials()
        if self.jump_info:
            conf_dict["jump_info"] = self.jump_info

        return conf_dict

    def get_identifier_and_fqn(self):
        return self.original_ds.get_identifier_and_fqn()

    def update_credentials(self, key: str):
        return self.original_ds.update_credentials(key)

    def override_schema(self, schema):
        return self.original_ds.override_schema(schema)

    def get_connect_args(self):
        return self.original_ds.get_connect_args()

    # delegator to the original datasource object. This should catch any methods not
    # overridden above (baseclass does not have specific methods that are part of
    # pg or snowflake implementations eg. host/port or warehouse etc)
    # and use the original datasource to generate responses
    def __getattr__(self, prop_or_func):
        # we are also delegating properties so we need to handle them separately
        # these are not functions but actual values so instead of the method wrapper
        # for functions below, these will be returned immediately
        if prop_or_func in self.available_delegated_props:
            # print("delegating property: {}".format(prop_or_func))
            value = getattr(self.original_ds, prop_or_func)
            return value

        # if the property is not a value, then check if its in the list of methods
        if prop_or_func in self.available_delegated_methods:
            # print("delegate method {} to original ds".format(prop_or_func))

            def method(*args):
                return getattr(self.original_ds, prop_or_func)(*args)

            return method

        else:
            raise AttributeError

    @contextmanager
    def get_bound_host_and_port(self) -> Generator[Dict[str, Any], None, None]:
        sshtunnel.DEFAULT_LOGLEVEL = sshtunnel.logging.DEBUG
        # allowing "SSH_PKEY_PW" to not exist because sometimes it private key can be passwordless
        if not all(
            k in self.jump_info for k in ["SSH_PKEY_PATH", "SSH_HOST", "SSH_USER"]
        ):
            raise ValueError("Missing required keys in jump_info")

        with sshtunnel.open_tunnel(
            (
                self.jump_info["SSH_HOST"],
                int(22),
            ),  # defaulting to bind port of https
            ssh_username=self.jump_info["SSH_USER"],
            ssh_pkey=self.jump_info["SSH_PKEY_PATH"],
            ssh_private_key_password=self.jump_info.get("SSH_PKEY_PW", None),
            remote_bind_address=(self.host, int(self.port)),  # type: ignore
        ) as tunnel:
            try:
                yield {"host": "0.0.0.0", "port": tunnel.local_bind_port}  # type: ignore
            except Exception as e:
                # re-raise exceptions raised in the context block
                raise e
