from __future__ import annotations

from typing import Union

from pydantic import StrictBool, StrictFloat, StrictInt, StrictStr

from kelvin.message.message import Message
from kelvin.message.msg_type import KMessageTypeData, KMessageTypeParameter
from kelvin.message.typing import AssetDataMessage  # noqa: F401


class Number(Message):
    TYPE_ = KMessageTypeData("number")

    type: KMessageTypeData = KMessageTypeData("number")
    payload: Union[StrictFloat, StrictInt] = 0.0


class String(Message):
    TYPE_ = KMessageTypeData("string")

    type: KMessageTypeData = KMessageTypeData("string")
    payload: StrictStr = ""


class Boolean(Message):
    TYPE_ = KMessageTypeData("boolean")

    type: KMessageTypeData = KMessageTypeData("boolean")
    payload: StrictBool = False


class NumberParameter(Message):
    TYPE_ = KMessageTypeParameter("number")

    type: KMessageTypeParameter = KMessageTypeParameter("number")
    payload: Union[StrictFloat, StrictInt] = 0.0


class StringParameter(Message):
    TYPE_ = KMessageTypeParameter("string")

    type: KMessageTypeParameter = KMessageTypeParameter("string")
    payload: StrictStr = ""


class BooleanParameter(Message):
    TYPE_ = KMessageTypeParameter("boolean")

    type: KMessageTypeParameter = KMessageTypeParameter("boolean")
    payload: StrictBool = False
