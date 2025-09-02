from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, model_validator
from typing_extensions import TypeAlias

from kelvin.config.manifest import IOStorage
from kelvin.krn import KRN, KRNAsset
from kelvin.message import Message
from kelvin.message.base_messages import ParameterType, PropertyType
from kelvin.message.msg_type import KMessageTypeRuntimeManifest


class ManifestDatastream(BaseModel):
    model_config = {"extra": "allow"}

    name: str
    data_type_name: Optional[str] = None
    semantic_type_name: Optional[str] = None
    unit_name: Optional[str] = None

    # legacy fields for backward compatibility
    primitive_type_name: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def prefill_resource(cls, data: dict[str, Any]) -> dict[str, Any]:
        if isinstance(data, dict):
            # If primitive_type_name is not set, try to infer it from data_type_name
            if not data.get("primitive_type_name"):
                data["primitive_type_name"] = data.get("data_type_name")
        return data


class WayEnum(str, Enum):
    output = "output"
    input_cc = "input-cc"
    input_cc_output = "input-cc+output"
    input = "input"
    output_cc = "output-cc"
    input_output_cc = "input+output-cc"


class SimpleValueGuardrail(BaseModel):
    value: float
    inclusive: bool = False


class RelativeValueType(str, Enum):
    value = "value"
    percentage = "percentage"


class RelativeValueGuardrail(BaseModel):
    value: float
    inclusive: bool = False
    type: RelativeValueType = RelativeValueType.value


class RelativeMinMax(BaseModel):
    min: Optional[RelativeValueGuardrail] = None
    max: Optional[RelativeValueGuardrail] = None


class RelativeGuardrail(BaseModel):
    increase: Optional[RelativeMinMax] = None
    decrease: Optional[RelativeMinMax] = None


class NumericGuardrail(BaseModel):
    min: Optional[SimpleValueGuardrail] = None
    max: Optional[SimpleValueGuardrail] = None
    relative: Optional[RelativeGuardrail] = None


class Guardrail(BaseModel):
    control_disabled: bool = False
    numeric: Optional[NumericGuardrail] = None


class ResourceDatastream(BaseModel):
    map_to: Optional[str] = None
    remote: Optional[bool] = None
    configuration: Dict = {}
    way: WayEnum = WayEnum.output
    storage: IOStorage = IOStorage.node_and_cloud
    guardrail: Optional[Guardrail] = None

    # legacy fields
    access: Literal["RO", "RW", "WO"] = "RO"
    owned: Optional[bool] = False

    @model_validator(mode="before")
    @classmethod
    def prefill_resource(cls, data: dict[str, Any]) -> dict[str, Any]:
        if isinstance(data, dict):
            # set "way" if not set for backward compatibility
            if data.get("way"):
                return data

            owned = data.get("owned", False)
            access = data.get("access", "RO")
            if owned:
                if access == "RO":
                    data["way"] = WayEnum.output
                elif access == "RW":
                    data["way"] = WayEnum.input_cc_output
                elif access == "WO":
                    data["way"] = WayEnum.input_cc
            else:
                if access == "RO":
                    data["way"] = WayEnum.input
                elif access == "RW":
                    data["way"] = WayEnum.input_output_cc
                elif access == "WO":
                    data["way"] = WayEnum.output_cc

        return data


class DQWayEnum(str, Enum):
    output = "output"
    intput = "input"


DQConfiguration: TypeAlias = Dict[str, Any]


class DataQuality(BaseModel):
    way: DQWayEnum = DQWayEnum.output
    datastreams: Dict[str, DQConfiguration] = {}
    configuration: DQConfiguration = {}


class Resource(BaseModel):
    resource: KRN
    datastreams: Dict[str, ResourceDatastream] = {}
    properties: Dict[str, PropertyType] = {}
    parameters: Dict[str, ParameterType] = {}
    data_quality: Dict[str, Any] = {}

    # Deprecated fields for backward compatibility
    type: str = ""
    name: str = ""

    @model_validator(mode="before")
    @classmethod
    def prefill_resource(cls, data: dict[str, Any]) -> dict[str, Any]:
        if isinstance(data, dict):
            # If resource is not provided, try to infer it from type and name
            if not data.get("resource") and data.get("type") == "asset" and data.get("name"):
                data["resource"] = KRNAsset(data["name"])
        return data


class CAWayEnum(str, Enum):
    intput_ca = "input-ca"
    output_ca = "output-ca"


class CustomAction(BaseModel):
    type: str
    way: CAWayEnum


class RuntimeManifestPayload(BaseModel):
    model_config = {"extra": "allow"}

    resources: List[Resource] = []
    configuration: Dict = {}
    datastreams: List[ManifestDatastream] = []
    custom_actions: List[CustomAction] = []


class RuntimeManifest(Message):
    TYPE_ = KMessageTypeRuntimeManifest()

    type: KMessageTypeRuntimeManifest = KMessageTypeRuntimeManifest()
    payload: RuntimeManifestPayload
