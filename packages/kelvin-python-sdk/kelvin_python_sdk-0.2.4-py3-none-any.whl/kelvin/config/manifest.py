from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Literal, Optional

from pydantic import Field

from kelvin.config.common import AppBaseConfig, ConfigBaseModel, CustomActionTypeStr, VersionStr
from kelvin.krn import KRN
from kelvin.message import ParameterType
from kelvin.message.msg_type import PrimitiveTypes


class RuntimeUpdateFlags(ConfigBaseModel):
    io: bool = False
    configuration: bool = False
    resource_parameters: bool = True
    resource_properties: bool = True


class DeploymentFlags(ConfigBaseModel):
    allowed_resources: List[KRN] = []


class Flags(ConfigBaseModel):
    spec_version: VersionStr
    enable_runtime_update: RuntimeUpdateFlags = RuntimeUpdateFlags()
    deployment: DeploymentFlags = DeploymentFlags()
    resources_required: Optional[bool] = None


class IOWay(str, Enum):
    output = "output"
    input_cc = "input-cc"
    input_cc_output = "input-cc+output"
    input = "input"
    output_cc = "output-cc"
    input_output_cc = "input+output-cc"


class DQWay(str, Enum):
    output = "output"
    input = "input"


class IOStorage(str, Enum):
    node_and_cloud = "node-and-cloud"
    node = "node"
    none = "none"


class IODefinition(ConfigBaseModel):
    name: str
    data_type: str
    unit: Optional[str]
    way: IOWay = IOWay.output
    storage: IOStorage = IOStorage.node_and_cloud


class DynamicIoOwnership(str, Enum):
    both = "both"
    owned = "owned"
    remote = "remote"


class DynamicIoType(str, Enum):
    both = "both"
    data = "data"
    control = "control"


class DynamicIODataTypes(ConfigBaseModel):
    name: str


class DynamicIODefinition(ConfigBaseModel):
    type_name: str
    ownership: DynamicIoOwnership = DynamicIoOwnership.both
    type: DynamicIoType = DynamicIoType.both
    data_types: List[str] = []


class CustomActionWay(str, Enum):
    input_ca = "input-ca"
    output_ca = "output-ca"


class ManifCustomAction(ConfigBaseModel):
    type: CustomActionTypeStr
    way: CustomActionWay


class ParamDefinition(ConfigBaseModel):
    name: str
    title: Optional[str] = None
    data_type: Optional[Literal[PrimitiveTypes.number, PrimitiveTypes.string, PrimitiveTypes.boolean]] = None
    default: Optional[ParameterType] = None


class IOSchema(ConfigBaseModel):
    type_name: str
    io_schema: dict = Field(default_factory=dict, alias="schema")


class SchemasDefinition(ConfigBaseModel):
    parameters: dict = {}
    configuration: dict = {}
    io_configurations: List[IOSchema] = []


class DeploymentType(str, Enum):
    standard = "standard"
    staged_instant_apply = "staged+instant-apply"
    staged_only = "staged-only"


class ClusterDefinition(ConfigBaseModel):
    name: str


class DeploymentTargetDefaults(ConfigBaseModel):
    type: Optional[str] = None
    cluster: Optional[ClusterDefinition] = None


class DeploymentDefaults(ConfigBaseModel):
    max_resources: Optional[int] = None
    deployment_type: Optional[DeploymentType] = None
    target: Optional[DeploymentTargetDefaults] = None


class IODatastreamMapping(ConfigBaseModel):
    io: str
    datastream: str


class AppDefaults(ConfigBaseModel):
    configuration: Dict[str, Any] = {}
    io_datastream_mapping: Optional[List[IODatastreamMapping]] = None


class DefaultsDefinition(ConfigBaseModel):
    deployment: Optional[DeploymentDefaults] = None
    app: Optional[AppDefaults] = None
    system: Optional[dict] = None


class ManifCustomDataQuality(ConfigBaseModel):
    name: str
    data_type: str
    way: DQWay
    datastreams: List[str] = []


class AppManifest(AppBaseConfig):
    flags: Optional[Flags] = None
    io: List[IODefinition] = []
    dynamic_io: List[DynamicIODefinition] = []
    parameters: List[ParamDefinition] = []
    schemas: SchemasDefinition = SchemasDefinition()
    defaults: DefaultsDefinition = DefaultsDefinition()
    custom_actions: List[ManifCustomAction] = []
    data_quality: List[ManifCustomDataQuality] = []
