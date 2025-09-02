from __future__ import annotations

from typing import Callable, List, Union

from typing_extensions import TypeGuard

from kelvin.krn import KRN, KRNAssetDataQuality, KRNAssetDataStream, KRNAssetDataStreamDataQuality
from kelvin.message import ControlChangeStatus, CustomAction, KMessageTypeData, Message
from kelvin.message.base_messages import CustomActionMsg
from kelvin.message.typing import (
    AssetDataMessage,
    AssetDataQualityMessage,
    AssetDataStreamDataQualityMessage,
)


def is_asset_data_message(msg: Message) -> TypeGuard[AssetDataMessage]:
    return isinstance(msg.resource, KRNAssetDataStream) and isinstance(msg.type, KMessageTypeData)


def is_data_message(msg: Message) -> bool:
    return isinstance(msg.type, KMessageTypeData)


def is_control_status_message(msg: Message) -> TypeGuard[ControlChangeStatus]:
    """Check if the message is a Control Change Status."""
    return isinstance(msg, ControlChangeStatus)


def resource_equals(resource: Union[KRN, List[KRN]]) -> Callable[[Message], TypeGuard[Message]]:
    def _check(msg: Message) -> TypeGuard[Message]:

        if not isinstance(msg.resource, KRN):
            return False

        if isinstance(resource, list):
            return msg.resource in resource

        return msg.resource == resource

    return _check


def input_equals(data: Union[str, List[str]]) -> Callable[[Message], TypeGuard[AssetDataMessage]]:
    def _check(msg: Message) -> TypeGuard[AssetDataMessage]:

        if not is_asset_data_message(msg):
            return False

        if isinstance(data, list):
            return msg.resource.data_stream in data

        return msg.resource.data_stream == data

    return _check


def asset_equals(asset: Union[str, List[str]]) -> Callable[[Message], TypeGuard[Message]]:
    def _check(msg: Message) -> TypeGuard[Message]:
        if not hasattr(msg.resource, "asset"):
            return False

        msg_asset = msg.resource.asset  # type: ignore

        if isinstance(asset, list):
            return msg_asset in asset

        return msg_asset == asset

    return _check


def is_custom_action(msg: Message) -> TypeGuard[CustomAction]:
    """Check if the message is a Custom Action Message."""
    return isinstance(msg, CustomActionMsg)


def is_asset_data_quality_message(msg: Message) -> TypeGuard[AssetDataQualityMessage]:
    """Check if the message is an Asset Data Quality Message."""
    return isinstance(msg.resource, KRNAssetDataQuality) and isinstance(msg.type, KMessageTypeData)


def is_asset_data_stream_quality_message(msg: Message) -> TypeGuard[AssetDataStreamDataQualityMessage]:
    """Check if the message is an Asset Data Stream Data Quality Message."""
    return isinstance(msg.resource, KRNAssetDataStreamDataQuality) and isinstance(msg.type, KMessageTypeData)


def is_data_quality_message(msg: Message) -> TypeGuard[AssetDataQualityMessage | AssetDataStreamDataQualityMessage]:
    """Check if the message is a Data Quality Message."""
    return isinstance(msg.type, KMessageTypeData) and (
        isinstance(msg.resource, KRNAssetDataQuality) or isinstance(msg.resource, KRNAssetDataStreamDataQuality)
    )
