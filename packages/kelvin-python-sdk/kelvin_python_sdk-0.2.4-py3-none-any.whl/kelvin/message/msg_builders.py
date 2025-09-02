from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from uuid import UUID, uuid4

from pydantic.dataclasses import dataclass
from pydantic.fields import Field

from kelvin.krn import KRN, KRNAppVersion, KRNAsset, KRNAssetDataStream, KRNAssetParameter
from kelvin.message import Message, ParameterType
from kelvin.message.base_messages import (
    ControlChangeAck,
    ControlChangeAckPayload,
    ControlChangeMsg,
    ControlChangePayload,
    CustomActionMsg,
    CustomActionPayload,
    CustomActionResultMsg,
    CustomActionResultPayload,
    DataTagMsg,
    DataTagPayload,
    EdgeParameter,
    ParametersMsg,
    ParametersPayload,
    RecommendationActions,
    RecommendationControlChange,
    RecommendationCustomAction,
    RecommendationMsg,
    RecommendationPayload,
    ReportedValues,
    ResourceParameters,
    StateEnum,
    ValuePoint,
)
from kelvin.message.evidences import BaseEvidence, Evidence
from kelvin.message.msg_type import KMessageTypeAction

TMessage = TypeVar("TMessage", bound=Message)
TBuilder = TypeVar("TBuilder", bound="MessageBuilder")


class MessageBuilder(Generic[TMessage]):
    _msg: Optional[TMessage] = Field(default=None, init=False, repr=False)

    def to_message(self) -> TMessage:
        return NotImplemented

    @classmethod
    def from_message(cls: Type[TBuilder], msg: TMessage) -> TBuilder:
        return NotImplemented


@dataclass
class ControlChange(MessageBuilder[ControlChangeMsg]):
    """Control change builder
    Use this helper class to build a Kelvin Control change.

    Args:
        resource (KRN): The kelvin resource targeted by the control change, represented by a KRN (usually
            KRNAssetDataStream)
        expiration_date (datetime | timedelta): The absolute time in the future when the Control Change expires. Provide
            either a absolute datetime or a timedelta from now
        payload (bool, int, float, str): The desired target value for the control change
        retries (int): Optional number of retries
        timeout (int): Optional timeout time (for retries)
        control_change_id (UUID): Optional UUID to set an specific ID for the control change
        from_value (ValuePoint): Optional initial value for the control change
        trace_id (str): Optional trace ID for the control change
    """

    resource: KRN
    expiration_date: Union[datetime, timedelta]
    payload: Any
    retries: Optional[int] = None
    timeout: Optional[int] = None
    control_change_id: Optional[UUID] = None
    from_value: Optional[ValuePoint] = None
    trace_id: Optional[str] = None

    def to_message(self) -> ControlChangeMsg:
        if isinstance(self.expiration_date, datetime):
            expiration = self.expiration_date
        else:
            expiration = datetime.now() + self.expiration_date

        return ControlChangeMsg(
            id=self.control_change_id if self.control_change_id is not None else uuid4(),
            trace_id=self.trace_id,
            resource=self.resource,
            payload=ControlChangePayload(
                timeout=self.timeout,
                retries=self.retries,
                expiration_date=expiration,
                payload=self.payload,
                from_value=self.from_value,
            ),
        )

    @classmethod
    def from_message(cls, msg: ControlChangeMsg) -> ControlChange:
        obj = cls(
            resource=msg.resource,  # type: ignore
            expiration_date=msg.payload.expiration_date,
            payload=msg.payload.payload,
            retries=msg.payload.retries,
            timeout=msg.payload.timeout,
            control_change_id=msg.id,
            from_value=msg.payload.from_value,
            trace_id=msg.trace_id,
        )
        obj._msg = msg
        return obj


@dataclass
class Recommendation(MessageBuilder[RecommendationMsg]):
    """Recommendation Builder. Use this helper class to build a Kelvin Recommendation.

    Args:
        resource (KRNAsset): The kelvin asset resource targeted by the recommendation
        type (str): the type of the recommendation, chose one from the available on the kelvin platform (eg generic,
            speed_inc, speed_dec, ...)
        expiration_date (datetime | timedelta): The absolute time in the future when the recommendation expires. Provide
            either a absolute datetime or a timedelta from now
        description (str): An optional description for the recommendation
        confidence (int): Optional confidence of the recommendation (from 1 to 4)
        control_changes (List[ControlChanges]): the list of ControlChanges associated with the recommendation
        metadata: (Dict[str, Any]): Optional metadata for the recommendation
        auto_accepted (bool): Sets the Recommendation as auto accepted. Default is False
        evidences (List[Evidence]): List of evidences associated with the recommendation
        custom_identifier (str): Optional custom identifier for the recommendation
        actions (List[CustomAction]): List of custom actions associated with the recommendation
        trace_id (str): Optional trace ID for the recommendation
    """

    resource: KRNAsset
    type: str
    expiration_date: Optional[Union[datetime, timedelta]] = None
    description: Optional[str] = None
    confidence: Optional[int] = Field(default=None, ge=1, le=4)
    control_changes: List[ControlChange] = Field(default_factory=list)
    metadata: Optional[Dict] = None
    auto_accepted: bool = False
    evidences: List[Evidence] = Field(default_factory=list)
    custom_identifier: Optional[str] = None
    actions: List[CustomAction] = Field(default_factory=list)
    trace_id: Optional[str] = None

    def to_message(self) -> RecommendationMsg:
        now = datetime.now()
        if self.expiration_date is None:
            rec_expiration_date = None
        elif isinstance(self.expiration_date, datetime):
            rec_expiration_date = self.expiration_date
        else:
            rec_expiration_date = now + self.expiration_date

        ccs = [
            RecommendationControlChange(
                retry=cc.retries,
                timeout=cc.timeout,
                expiration_date=(
                    cc.expiration_date if isinstance(cc.expiration_date, datetime) else now + cc.expiration_date
                ),
                payload=cc.payload,
                resource=cc.resource,
                control_change_id=cc.control_change_id,
                from_value=cc.from_value,
                trace_id=cc.trace_id,
            )
            for cc in self.control_changes
        ]

        actions = [
            RecommendationCustomAction(
                type=action.type,
                resource=action.resource,
                trace_id=action.trace_id,
                title=action.title,
                description=action.description,
                expiration_date=(
                    action.expiration_date
                    if isinstance(action.expiration_date, datetime)
                    else now + action.expiration_date
                ),
                payload=action.payload,
            )
            for action in self.actions
        ]

        return RecommendationMsg(
            resource=self.resource,
            trace_id=self.trace_id,
            payload=RecommendationPayload(
                resource=self.resource,
                type=self.type,
                description=self.description,
                expiration_date=rec_expiration_date,
                confidence=self.confidence,
                actions=RecommendationActions(control_changes=ccs, custom_actions=actions),
                metadata=self.metadata,
                state="auto_accepted" if self.auto_accepted is True else None,
                evidences=[BaseEvidence(type=ev._TYPE, payload=ev) for ev in self.evidences],
                custom_identifier=self.custom_identifier,
                trace_id=self.trace_id,
            ),
        )


@dataclass
class AppParameter:
    """Asset Parameter Helper.

    Args:
        resource (KRNAssetParameter): Kelvin Resource name for the target Asset Parameter
        value (Union[bool, int, float, string]): parameter value
        comment (Optional[str]): optional comment for parameter change
    """

    resource: KRNAssetParameter
    value: ParameterType
    comment: Optional[str] = None


class AssetParameter(AppParameter):
    """[Deprecated] Use AppParameter instead
    Asset Parameter Helper.

    Args:
        resource (KRNAssetParameter): Kelvin Resource name for the target Asset Parameter
        value (Union[bool, int, float, string]): parameter value
        comment (Optional[str]): optional comment for parameter change
    """


@dataclass
class AppParameters(MessageBuilder):
    """Parameters Builder. Set application parameters in bulk.

    Args:
        resource (Optional[KRNAppVersion]): Optional Kelvin Resource name for the target App Version.
            Defaults to current app.
        parameters (List[AssetParameters]): list of single asset parameters
    """

    parameters: List[AppParameter]
    resource: Optional[KRNAppVersion] = None

    def to_message(self) -> ParametersMsg:
        asset_params: Dict[str, List[EdgeParameter]] = {}
        for asset_param in self.parameters:
            asset_params.setdefault(asset_param.resource.asset, []).append(
                EdgeParameter(name=asset_param.resource.parameter, value=asset_param.value, comment=asset_param.comment)
            )

        param_models = [
            ResourceParameters(resource=KRNAsset(asset), parameters=params) for asset, params in asset_params.items()
        ]

        return ParametersMsg(resource=self.resource, payload=ParametersPayload(resource_parameters=param_models))


class AssetParameters(AppParameters):
    """[Deprecated] Use AppParameters instead
    Parameters Builder. Set application parameters in bulk.

    Args:
        resource (Optional[KRNAppVersion]): Optional Kelvin Resource name for the target App Version.
            Defaults to current app.
        parameters (List[AssetParameters]): list of single asset parameters
    """


@dataclass
class DataTag(MessageBuilder):
    """Data Tag.

    Args:
       start_date (datetime): The start date of the data tag.
       tag_name (str): The name of the data tag.
       resource (KRNAsset): The asset resource associated with the data tag.
       end_date (Optional[datetime]): The end date of the data tag. If not specified, the data tag is
       considered one point in time, the start_date.
       contexts (Optional[List[KRN]]): The list of contexts associated with the data tag.
       description (Optional[str]): The description of the data tag. Truncated to 256 characters.
    """

    start_date: datetime
    tag_name: str
    resource: KRNAsset
    end_date: Optional[datetime] = None
    contexts: Optional[List[KRN]] = None
    description: Optional[str] = None

    def to_message(self) -> DataTagMsg:
        end_date = self.end_date or self.start_date
        description = self.description[:256] if self.description else None

        return DataTagMsg(
            resource=self.resource,
            payload=DataTagPayload(
                start_date=self.start_date,
                end_date=end_date,
                tag_name=self.tag_name,
                resource=self.resource,
                description=description,
                contexts=self.contexts,
            ),
        )


@dataclass
class ControlAck(MessageBuilder):
    """Control Change Ack

    Args:
        resource (KRNAssetDataStream): The resource associated with the control change
        state (StateEnum): The state of the control change
        message (Optional[str]): Optional message
        before (Optional[ValuePoint]): Optional value point before the control change
        after (Optional[ValuePoint]): Optional value point after the control change
        metadata (Optional[Dict]): Optional metadata for the control change ack
    """

    resource: KRNAssetDataStream
    state: StateEnum
    message: Optional[str] = None
    before: Optional[ValuePoint] = None
    after: Optional[ValuePoint] = None
    metadata: Optional[Dict] = None

    def to_message(self) -> ControlChangeAck:
        return ControlChangeAck(
            resource=self.resource,
            payload=ControlChangeAckPayload(
                state=self.state,
                message=self.message,
                reported=ReportedValues(before=self.before, after=self.after) if self.before or self.after else None,
                metadata=self.metadata,
            ),
        )


@dataclass
class CustomAction(MessageBuilder[CustomActionMsg]):
    """Custom Action Builder. Use this helper class to build a Kelvin custom action.

    Args:
        resource (KRN): The kelvin resource targeted by the action, represented by a KRN (usually KRNAssetData)
        type (str): The type of the action
        title (str): The title of the action
        description (Optional[str]): Optional description for the action
        expiration_date (Union[datetime, timedelta]): Expiration date for the action.
            Provide either a absolute datetime or a timedelta from now
        payload (Dict): Optional payload for the action
        trace_id (Optional[str]): Optional trace ID for the action
        custom_action_id (UUID): Optional UUID to set an specific ID for the control change
    """

    resource: KRN
    type: str
    title: str
    expiration_date: Union[datetime, timedelta]
    description: Optional[str] = None
    payload: Dict = Field(default_factory=dict)
    trace_id: Optional[str] = None
    custom_action_id: Optional[UUID] = None

    def to_message(self) -> CustomActionMsg:
        if isinstance(self.expiration_date, timedelta):
            expiration = datetime.now() + self.expiration_date
        else:
            expiration = self.expiration_date

        return CustomActionMsg(
            id=self.custom_action_id if self.custom_action_id is not None else uuid4(),
            type=KMessageTypeAction(action_type=self.type),
            trace_id=self.trace_id,
            resource=self.resource,
            payload=CustomActionPayload(
                title=self.title,
                description=self.description,
                expiration_date=expiration,
                payload=self.payload,
            ),
        )

    @classmethod
    def from_message(cls, msg: CustomActionMsg) -> CustomAction:
        if not isinstance(msg.type, KMessageTypeAction):
            raise ValueError(f"Invalid message type: {msg.type}")

        obj = cls(
            resource=msg.resource,  # type: ignore
            type=msg.type.type,
            title=msg.payload.title,
            description=msg.payload.description,
            expiration_date=msg.payload.expiration_date,
            payload=msg.payload.payload,
            trace_id=msg.trace_id,
            custom_action_id=msg.id,
        )
        obj._msg = msg
        return obj

    def result(
        self, success: bool, message: Optional[str] = None, metadata: Optional[Dict] = None
    ) -> CustomActionResult:
        """Create a result for the custom action.

        Args:
            success (bool): Whether the action was successful
            message (Optional[str]): Optional message
            metadata (Optional[Dict]): Optional metadata for the action ack

        Returns:
            CustomActionAck: The custom action ack
        """
        if self._msg is None:
            raise ValueError("Can't build CustomActionAck, internal _msg not set")

        return CustomActionResult(
            resource=self.resource,
            action_id=self._msg.id,
            success=success,
            message=message,
            metadata=metadata,
            trace_id=self.trace_id,
        )


@dataclass
class CustomActionResult(MessageBuilder[CustomActionResultMsg]):
    """Custom Action Result Builder. Use this helper class to build a Kelvin custom action ack.
    Args:
        resource (KRN): The kelvin resource targeted by the action, represented by a KRN (usually
            KRNAssetDataStream)
        action_id (UUID): The ID of the action
        success (bool): Whether the action was successful
        message (Optional[str]): Optional message
        metadata: Dict[str, Any]: Optional metadata for the action ack
        trace_id (Optional[str]): Optional trace ID for the action
    """

    resource: KRN
    action_id: UUID
    success: bool
    message: Optional[str] = None
    metadata: Optional[Dict] = None
    trace_id: Optional[str] = None

    def to_message(self) -> CustomActionResultMsg:
        return CustomActionResultMsg(
            resource=self.resource,
            trace_id=self.trace_id,
            payload=CustomActionResultPayload(
                id=self.action_id,
                success=self.success,
                message=self.message,
                metadata=self.metadata,
            ),
        )

    @classmethod
    def from_message(cls, msg: CustomActionResultMsg) -> CustomActionResult:
        obj = cls(
            resource=msg.resource,  # type: ignore
            action_id=msg.payload.id,
            success=msg.payload.success,
            message=msg.payload.message,
            metadata=msg.payload.metadata,
            trace_id=msg.trace_id,
        )
        obj._msg = msg
        return obj


BUILDER_REGISTRY: Dict[Type[Message], Type[MessageBuilder]] = {
    ControlChangeMsg: ControlChange,
    CustomActionMsg: CustomAction,
    CustomActionResultMsg: CustomActionResult,
}


def convert_message(msg: Message) -> Optional[MessageBuilder]:
    """Convert a message to its builder class.

    Args:
        msg (Message): The message to convert

    Returns:
        Optional[MessageBuilder]: The converted message builder
    """
    if msg.__class__ in BUILDER_REGISTRY:
        return BUILDER_REGISTRY[msg.__class__].from_message(msg)
    return None
