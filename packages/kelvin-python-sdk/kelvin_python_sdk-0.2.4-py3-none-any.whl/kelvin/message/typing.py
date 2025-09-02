from __future__ import annotations

from kelvin.krn import KRNAssetDataQuality, KRNAssetDataStream, KRNAssetDataStreamDataQuality
from kelvin.message import KMessageTypeData, Message


class AssetDataMessage(Message):
    type: KMessageTypeData
    resource: KRNAssetDataStream


class AssetDataQualityMessage(Message):
    type: KMessageTypeData
    resource: KRNAssetDataQuality


class AssetDataStreamDataQualityMessage(Message):
    type: KMessageTypeData
    resource: KRNAssetDataStreamDataQuality
