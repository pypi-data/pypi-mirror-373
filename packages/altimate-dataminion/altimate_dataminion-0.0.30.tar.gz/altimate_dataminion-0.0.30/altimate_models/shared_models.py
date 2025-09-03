from enum import Enum
from typing import Any, Dict, List, Optional, Text, Union

from pydantic.v1 import BaseModel, Field


# TODO: This needs to be removed in favor of Policy. Relevant parts in CLI also needs to be updated.
class TableMeta(BaseModel):
    database: Optional[Text]
    db_schema: Optional[Text] = Field(alias="schema")
    table: Optional[Text]


class Term(BaseModel):
    term_index: int
    metric: Text
    params: Dict[Text, Any]


class ResourceType(Enum):
    FILE = "file"
    TABLE = "table"


class TableResource(BaseModel):
    database: Text
    db_schema: Optional[Text] = Field(alias="schema", default=None)
    table: Optional[Text] = None


class S3Resource(BaseModel):
    bucket: Text
    path: Text
    format: Text
    options: Optional[Dict[Text, Any]]


class Resource(BaseModel):
    resource_type: ResourceType
    resource: Union[TableResource, S3Resource]
    filters: Optional[Text] = None


class Policy(BaseModel):
    policy_index: int
    policy_type: Text
    resources: List[Resource]
    filters: Optional[Text]
    terms: List[Term]

    @property
    def resource0(self):
        return self.resources[0]

    @property
    def resource1(self):
        return self.resources[1]


class ProfileConfig(BaseModel):
    policies: List[Policy]

class PrivateKeyType(Enum):
    PEM = "pem"
    DER = "der"
    