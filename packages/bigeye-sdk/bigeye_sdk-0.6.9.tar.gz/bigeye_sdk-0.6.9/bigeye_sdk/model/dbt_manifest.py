from typing import Dict, List, Optional
from enum import Enum

from pydantic.v1 import BaseModel, validator, Field


class DbtResourceType(str, Enum):
    model = 'model'
    analysis = 'analysis'
    test = 'test'
    operation = 'operation'
    seed = 'seed'
    source = 'source'


class DbtMeta(BaseModel):
    owner: Optional[str]


class NodeConfig(BaseModel):
    meta: Optional[DbtMeta] = None


class Node(BaseModel):
    unique_id: str
    path: str
    resource_type: DbtResourceType
    description: str
    config: NodeConfig
    database: str
    schema_name: str = Field(alias='schema')
    name: str


class DbtManifest(BaseModel):
    nodes: Dict["str", Node]
    sources: Dict["str", Node]

    @validator('nodes', 'sources')
    def filter(cls, val):
        return {k: v for k, v in val.items() if v.resource_type.value in ('model', 'seed', 'source')}
