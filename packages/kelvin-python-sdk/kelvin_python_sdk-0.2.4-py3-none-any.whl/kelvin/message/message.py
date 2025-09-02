from __future__ import annotations

from datetime import datetime
from typing import Any, ClassVar, Dict, Optional, Type
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_serializer
from typing_extensions import Self

from kelvin.krn import KRN, KRNAssetDataStream
from kelvin.message.msg_type import KMessageType, KMessageTypeData, KMessageTypePrimitive
from kelvin.message.utils import to_rfc3339_timestamp

# Set to True to fail when parsing unknown message types
FAIL_ON_UNKNOWN_TYPES = False


class Message(BaseModel):
    MESSAGE_TYPES_: ClassVar[Dict[KMessageType, Type["Message"]]] = {}
    TYPE_: ClassVar[Optional[KMessageType]] = None

    type: KMessageType
    resource: Optional[KRN] = None
    id: UUID = Field(default_factory=uuid4)
    trace_id: Optional[str] = None
    source: Optional[KRN] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now().astimezone())

    payload: Any = None

    def __init_subclass__(cls) -> None:
        if cls.TYPE_:
            Message.MESSAGE_TYPES_[cls.TYPE_] = cls

    def __new__(cls, **kwargs: Any) -> Message:  # pyright: ignore
        """Initialise message."""

        if cls.TYPE_:
            MSG_T = cls
        else:
            msg_type = cls._get_msg_type_from_payload(**kwargs)
            if msg_type is None and FAIL_ON_UNKNOWN_TYPES is True:
                raise ValueError("Missing message type") from None

            # trying to match full type eg "data;pt=number"
            MSG_T = Message.MESSAGE_TYPES_.get(msg_type, None)  # type: ignore
            if MSG_T is None:
                if msg_type is not None:
                    # trying to match message type with no components eg "data"
                    msg_type.components = {}
                MSG_T = Message.MESSAGE_TYPES_.get(msg_type, Message)  # type: ignore

        obj = super().__new__(MSG_T)
        return obj

    def __init__(self, **kwargs: Any) -> None:  # pyright: ignore
        """
        Create a kelvin Message.

        Parameters
        ----------
        id : str, optional
            UUID of the message. Optional, auto generated if not provided.
        type : KMessageType
            Message Type
        trace_id : str, optional
            Optional trace id. UUID
        source : KRN, optional
            Identifies the source of the message.
        timestamp : datetime, optional
            Sets a timestamp for the message. If not provided current time is used.
        resource : KRN, optional
            Sets a resource that the message relates to.
        payload : Any
            Payload of the message. Specific for each message sub type.
        """

        new_kwargs = kwargs
        if kwargs.get("data_type"):
            new_kwargs = self._convert_message_v1(**kwargs)
        elif kwargs.get("_"):
            new_kwargs = self._convert_message_v0(**kwargs)

        if new_kwargs.get("type") is None and self.TYPE_:
            new_kwargs["type"] = self.TYPE_

        super().__init__(**new_kwargs)

    def dict(
        self,
        by_alias: bool = True,
        exclude_none: bool = True,
        exclude_unset: bool = False,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Generate a dictionary representation of the model."""

        return super().model_dump(by_alias=by_alias, exclude_none=exclude_none, exclude_unset=exclude_unset, **kwargs)

    def json(
        self,
        by_alias: bool = True,
        exclude_none: bool = True,
        exclude_unset: bool = False,
        **kwargs: Any,
    ) -> str:
        """Generate a dictionary representation of the model."""

        return super().model_dump_json(
            by_alias=by_alias, exclude_none=exclude_none, exclude_unset=exclude_unset, serialize_as_any=True, **kwargs
        )

    def encode(self) -> bytes:
        """Encode message"""
        return self.__pydantic_serializer__.to_json(self, by_alias=True, exclude_none=True, serialize_as_any=True)

    @classmethod
    def decode(cls, data: bytes) -> Self:
        return cls.model_validate_json(data)

    @staticmethod
    def _convert_message_v1(**kwargs: Dict) -> Dict:
        result: Dict[str, Any] = {
            "id": kwargs.get("id", None),
            "timestamp": kwargs.get("timestamp", None),
        }

        asset = kwargs.get("asset_name", None)
        metric = kwargs.get("name", None)
        if asset and metric:
            result["resource"] = KRNAssetDataStream(asset, metric)  # type: ignore

        result["type"] = KMessageTypePrimitive(icd=str(kwargs.get("data_type")))

        source = kwargs.get("source", None)
        if source:
            result["source"] = "krn:wl:" + str(source)

        result["payload"] = kwargs.get("payload")

        return result

    @staticmethod
    def _convert_message_v0(**kwargs: Dict) -> Dict:
        result: Dict[str, Any] = {}

        header = kwargs.pop("_")

        asset = header.get("asset_name", None) or ""
        metric = header.get("name", None) or ""
        # resource should not have empty asset but kelvin-app uses v0 messages with no asset
        result["resource"] = KRNAssetDataStream(asset, metric)

        result["type"] = KMessageTypePrimitive(icd=str(kwargs.get("data_type")))

        source = header.get("source", None)
        if source:
            if isinstance(source, dict):
                source = source.get("node_name", "") + "/" + source.get("workload_name", "")
            result["source"] = "krn:wl:" + source

        timestamp_ns = header.get("time_of_validity", None)
        if timestamp_ns is not None:
            result["timestamp"] = datetime.fromtimestamp(timestamp_ns / 1e9).astimezone()

        id = timestamp_ns = header.get("id", None)
        if id:
            result["id"] = id

        # the remaining kwargs are payload
        result["payload"] = kwargs

        return result

    @staticmethod
    def _get_msg_type_from_payload(**kwargs: Any) -> Optional[KMessageType]:
        # "type" from v2 or "data_type" from v1 or "_.type" from v0
        v2_type = str(kwargs.get("type", ""))
        if v2_type:
            return KMessageType.from_string(v2_type)

        icd = kwargs.get("data_type") or kwargs.get("_", {}).get("type")
        if icd:
            return KMessageTypeData(primitive="object", icd=icd)

        return None

    @field_serializer("timestamp")
    def serialize_timestamp(self, ts: datetime) -> str:
        return to_rfc3339_timestamp(ts)
