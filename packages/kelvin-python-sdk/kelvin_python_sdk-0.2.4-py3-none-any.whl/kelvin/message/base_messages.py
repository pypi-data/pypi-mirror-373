from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field, StrictBool, StrictFloat, StrictInt, StrictStr, field_serializer
from typing_extensions import Literal, TypeAlias

from kelvin.krn import KRN, KRNAsset
from kelvin.message.evidences import BaseEvidence
from kelvin.message.message import Message
from kelvin.message.msg_type import (
    KMessageTypeAction,
    KMessageTypeActionAck,
    KMessageTypeControl,
    KMessageTypeControlAck,
    KMessageTypeControlStatus,
    KMessageTypeData,
    KMessageTypeDataTag,
    KMessageTypeParameters,
    KMessageTypeRecommendation,
)
from kelvin.message.utils import to_rfc3339_timestamp

ParameterType: TypeAlias = Union[StrictBool, StrictInt, StrictFloat, StrictStr]
PropertyType: TypeAlias = Union[StrictBool, StrictInt, StrictFloat, StrictStr]


class ValuePoint(BaseModel):
    value: Any
    timestamp: datetime
    source: Optional[str] = None

    @field_serializer("timestamp")
    def serialize_timestamp(self, ts: datetime) -> str:
        return to_rfc3339_timestamp(ts)


class ControlChangePayload(BaseModel):
    model_config = {"populate_by_name": True}

    timeout: Optional[int] = Field(None, description="Timeout for retries")
    retries: Optional[int] = Field(None, description="Max retries")
    expiration_date: datetime = Field(description="Absolute expiration Date in UTC")
    payload: Any = Field(None, description="Control Change payload")

    from_value: Optional[ValuePoint] = Field(
        None, description="Optional value of the datastream at the moment of the creation", alias="from"
    )

    @field_serializer("expiration_date")
    def serialize_timestamp(self, ts: datetime) -> str:
        return to_rfc3339_timestamp(ts)


class ControlChangeMsg(Message):
    """Generic Control Change Message"""

    TYPE_ = KMessageTypeControl()

    type: KMessageTypeControl = KMessageTypeControl()
    payload: ControlChangePayload


class StateEnum(str, Enum):
    ready = "ready"
    sent = "sent"
    failed = "failed"
    processed = "processed"
    applied = "applied"
    rejected = "rejected"


class ReportedValues(BaseModel):
    before: Optional[ValuePoint] = None
    after: Optional[ValuePoint] = None


class ControlChangeStatusPayload(BaseModel):
    state: StateEnum
    message: Optional[str] = None
    reported: Optional[ReportedValues] = None

    # control_change_id required, kept optional for backward compatibility
    control_change_id: Optional[UUID] = None
    metadata: Optional[Dict] = None


class ControlChangeStatus(Message):
    """Control Change Status"""

    TYPE_ = KMessageTypeControlStatus()

    type: KMessageTypeControlStatus = KMessageTypeControlStatus()
    payload: ControlChangeStatusPayload


class ControlChangeAckPayload(ControlChangeStatusPayload):
    """Control Change Ack Payload"""


class ControlChangeAck(Message):
    """Control Change Ack"""

    TYPE_ = KMessageTypeControlAck()

    type: KMessageTypeControlAck = KMessageTypeControlAck()
    payload: ControlChangeAckPayload


class SensorDataPayload(BaseModel):
    data: List[float] = Field(..., description="Array of sensor measurements.", min_length=1)
    sample_rate: float = Field(..., description="Sensor sample-rate in Hertz.", gt=0.0)


class SensorDataMsg(Message):
    """Sensor data."""

    TYPE_ = KMessageTypeData("object", "kelvin.sensor_data")

    type: KMessageTypeData = KMessageTypeData("object", "kelvin.sensor_data")
    payload: SensorDataPayload


class EdgeParameter(BaseModel):
    name: str
    value: ParameterType
    comment: Optional[str] = None


class ResourceParameters(BaseModel):
    resource: KRN
    parameters: List[EdgeParameter]


class ParametersPayload(BaseModel):
    source: Optional[KRN] = None
    resource_parameters: List[ResourceParameters]


class ParametersMsg(Message):
    TYPE_ = KMessageTypeParameters()

    type: KMessageTypeParameters = KMessageTypeParameters()
    payload: ParametersPayload


class DataTagPayload(BaseModel):
    start_date: datetime
    end_date: datetime
    tag_name: str
    resource: KRNAsset
    description: Optional[str] = Field(None, max_length=256)
    contexts: Optional[List[KRN]] = None
    source: Optional[KRN] = None

    @field_serializer("start_date", "end_date")
    def serialize_timestamp(self, ts: datetime) -> str:
        return to_rfc3339_timestamp(ts)


class DataTagMsg(Message):
    TYPE_ = KMessageTypeDataTag()

    type: KMessageTypeDataTag = KMessageTypeDataTag()
    resource: KRNAsset
    payload: DataTagPayload


class CustomActionPayload(BaseModel):
    title: str
    expiration_date: datetime
    description: Optional[str] = None
    payload: Dict = {}

    @field_serializer("expiration_date")
    def serialize_timestamp(self, ts: datetime) -> str:
        return to_rfc3339_timestamp(ts)


class CustomActionMsg(Message):
    TYPE_ = KMessageTypeAction()

    type: KMessageTypeAction = KMessageTypeAction()
    payload: CustomActionPayload


class CustomActionResultPayload(BaseModel):
    id: UUID
    success: bool
    message: Optional[str] = None
    metadata: Optional[Dict] = None


class CustomActionResultMsg(Message):
    TYPE_ = KMessageTypeActionAck()

    type: KMessageTypeActionAck = KMessageTypeActionAck()
    payload: CustomActionResultPayload


class RecommendationControlChange(ControlChangePayload):
    retries: Optional[int] = Field(None, description="Max retries", alias="retry")
    state: Optional[str] = None
    resource: Optional[KRN] = None
    control_change_id: Optional[UUID] = Field(None, description="Control Change ID")
    trace_id: Optional[str] = None


class RecommendationCustomAction(CustomActionPayload):
    type: str
    resource: KRN
    custom_action_id: Optional[UUID] = None
    trace_id: Optional[str] = None


class RecommendationActions(BaseModel):
    control_changes: List[RecommendationControlChange] = []
    custom_actions: List[RecommendationCustomAction] = []


class RecommendationPayload(BaseModel):
    source: Optional[KRN] = None
    resource: KRN
    type: str
    description: Optional[str] = None
    confidence: Optional[int] = Field(None, ge=1, le=4)
    expiration_date: Optional[datetime] = None
    actions: RecommendationActions = RecommendationActions()
    metadata: Optional[Dict] = None
    state: Optional[Literal["pending", "auto_accepted"]] = None
    evidences: List[BaseEvidence] = []
    custom_identifier: Optional[str] = None
    trace_id: Optional[str] = None

    @field_serializer("expiration_date")
    def serialize_timestamp(self, ts: datetime) -> str:
        return to_rfc3339_timestamp(ts)


class RecommendationMsg(Message):
    TYPE_ = KMessageTypeRecommendation()

    type: KMessageTypeRecommendation = KMessageTypeRecommendation()
    payload: RecommendationPayload
