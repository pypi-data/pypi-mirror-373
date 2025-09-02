from __future__ import annotations

from enum import Enum
from typing import Any, Dict, Optional, Type

from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema
from typing_extensions import Self


class KMessageType:
    """Kelvin Message Type representation"""

    _SUBTYPES: Dict[str, Type[KMessageType]] = {}
    _TYPE: str = ""

    msg_type: str
    components: Dict[str, str]

    def __init_subclass__(cls) -> None:
        if cls._TYPE:
            KMessageType._SUBTYPES[cls._TYPE] = cls

    def __init__(self, msg_type: Optional[str] = None, components: Dict[str, str] = {}) -> None:
        self.msg_type = msg_type or self._TYPE
        self.components = components

    @classmethod
    def __get_pydantic_core_schema__(cls, source: Any, handler: GetCoreSchemaHandler) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls.validate,
            handler(Any),
            serialization=core_schema.plain_serializer_function_ser_schema(cls.encode),
        )

    @classmethod
    def validate(cls, v: Any) -> KMessageType:
        if isinstance(v, str):
            return cls.from_string(v)

        if isinstance(v, cls):
            return v

        raise TypeError("Invalid type for KMessageType. KMessageType or string required.")

    @classmethod
    def from_krn(cls, msg_type: str, components: Dict[str, str]) -> KMessageType:
        T = KMessageType._SUBTYPES.get(msg_type, None)
        if T is not None:
            return T.from_krn(msg_type, components)

        return cls(msg_type, components)

    @classmethod
    def from_string(cls, v: str) -> Self:
        if not isinstance(v, str):
            raise TypeError("string required")

        msg_type, *components = v.split(";")
        components_dict = {}
        for component in components:
            try:
                key, *value = component.split("=", 1)
            except ValueError as exc:
                raise ValueError(f"Invalid type '{v}'. Expected format '<type>;<key>[=<value>]'") from exc
            components_dict[key] = value[0] if len(value) else ""

        return cls.from_krn(msg_type, components_dict)  # type: ignore

    def __eq__(self, other: Any) -> bool:
        if type(self) is not type(other):
            return False

        return self.msg_type == other.msg_type and self.components == other.components

    def __hash__(self) -> int:
        return hash((self.msg_type,) + tuple(sorted(self.components.items())))

    def __str__(self) -> str:
        return ";".join([self.msg_type, *[f"{key}={value}" for key, value in self.components.items() if value]])

    def __repr__(self) -> str:
        components_str = ";".join(f"{key}={value}" for key, value in self.components.items())
        return f"{self.__class__.__name__}('{self.msg_type}', '{components_str}')"

    def encode(self) -> str:
        return str(self)


class PrimitiveTypes(str, Enum):
    number = "number"
    string = "string"
    boolean = "boolean"
    object = "object"


class KMessageTypePrimitive(KMessageType):
    primitive: PrimitiveTypes
    icd: Optional[str] = None

    def __init__(self, primitive: str = "object", icd: Optional[str] = None):
        components: Dict[str, str] = {"pt": primitive}  # type: ignore
        if icd is not None:
            components["icd"] = icd
        super().__init__(self._TYPE, components)
        self.primitive = PrimitiveTypes[primitive]
        self.icd = icd

    @classmethod
    def from_krn(cls, msg_type: str, components: Optional[Dict[str, str]]) -> Self:
        if msg_type != cls._TYPE:
            raise ValueError(f"Error parsing {cls.__name__}. Expected {cls._TYPE}, got {msg_type}")

        primitive = components.get("pt", "object") if components else "object"
        icd = components.get("icd", None) if components else None

        return cls(primitive, icd)  # type: ignore

    def __str__(self) -> str:
        if self.primitive == PrimitiveTypes.object:
            return f"{self.msg_type};icd={self.icd}"

        return super().__str__()


class KMessageTypeData(KMessageTypePrimitive):
    _TYPE = "data"


class KMessageTypeParameter(KMessageTypePrimitive):
    _TYPE = "parameter"


class KMessageTypeControl(KMessageType):
    _TYPE = "control"

    @classmethod
    def from_krn(cls, _: str, __: Optional[Dict[str, str]]) -> Self:
        return cls(cls._TYPE, {})


class KMessageTypeControlStatus(KMessageType):
    _TYPE = "control-status"

    @classmethod
    def from_krn(cls, _: str, __: Optional[Dict[str, str]]) -> Self:
        return cls(cls._TYPE)


class KMessageTypeControlAck(KMessageType):
    _TYPE = "control-ack"

    @classmethod
    def from_krn(cls, _: str, __: Optional[Dict[str, str]]) -> Self:
        return cls(cls._TYPE)


class KMessageTypeRecommendation(KMessageType):
    _TYPE = "recommendation"

    @classmethod
    def from_krn(cls, _: str, __: Optional[Dict[str, str]]) -> Self:
        return cls(cls._TYPE)


class KMessageTypeParameters(KMessageType):
    _TYPE = "parameters"

    @classmethod
    def from_krn(cls, _: str, __: Optional[Dict[str, str]]) -> Self:
        return cls(cls._TYPE)


class KMessageTypeRuntimeManifest(KMessageType):
    _TYPE = "runtime_manifest"

    @classmethod
    def from_krn(cls, _: str, __: Optional[Dict[str, str]]) -> Self:
        return cls(cls._TYPE)


class KMessageTypeDataTag(KMessageType):
    _TYPE = "datatag"

    @classmethod
    def from_krn(cls, _: str, __: Optional[Dict[str, str]]) -> Self:
        return cls(cls._TYPE)


class KMessageTypeAction(KMessageType):
    _TYPE = "custom-action-create"

    type: str

    def __init__(self, action_type: str = ""):
        components = {"type": action_type} if action_type else {}
        super().__init__(self._TYPE, components)
        self.type = action_type

    @classmethod
    def from_krn(cls, msg_type: str, components: Dict[str, str]) -> Self:
        if msg_type != cls._TYPE:
            raise ValueError(f"Error parsing {cls.__name__}. Expected {cls._TYPE}, got {msg_type}")

        action_type = components.get("type", "")

        return cls(action_type)  # type: ignore


class KMessageTypeActionAck(KMessageType):
    _TYPE = "custom-action-result"

    @classmethod
    def from_krn(cls, _: str, __: Optional[Dict[str, str]]) -> Self:
        return cls(cls._TYPE)
