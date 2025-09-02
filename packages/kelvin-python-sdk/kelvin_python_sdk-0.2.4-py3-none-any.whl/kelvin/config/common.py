from __future__ import annotations

import json
import os
from enum import Enum
from pathlib import Path
from typing import Any, List, Literal, Optional

from pydantic import BaseModel, StringConstraints
from typing_extensions import Annotated, override

NameDNS = Annotated[str, StringConstraints(pattern="^[a-z0-9]([-a-z0-9]*[a-z0-9])?$")]
VersionStr = Annotated[
    str,
    StringConstraints(
        pattern="^([0-9]+)\\.([0-9]+)\\.([0-9]+)(?:-([0-9A-Za-z-]+(?:\\.[0-9A-Za-z-]+)*))?(?:\\+[0-9A-Za-z-]+)?$"
    ),
]
CustomActionTypeStr = Annotated[str, StringConstraints(pattern="^[a-zA-Z0-9]([-_ .a-zA-Z0-9]*[a-zA-Z0-9])?$")]


class ConfigError(Exception):
    pass


class ConfigBaseModel(BaseModel):
    model_config = {"populate_by_name": True}

    @override
    def model_dump(  # type: ignore[override]
        self,
        mode: Literal["json", "python"] | str = "json",
        by_alias: bool = True,
        exclude_unset: bool = True,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        serialize_as_any: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        return super().model_dump(
            mode=mode,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            serialize_as_any=serialize_as_any,
            **kwargs,
        )


class AppTypes(str, Enum):
    importer = "importer"
    exporter = "exporter"
    app = "app"
    docker = "docker"

    # legacy - deprecated
    kelvin_app = "kelvin"
    bridge = "bridge"
    legacy_docker = "legacy_docker"


class PrimitiveTypes(str, Enum):
    number = "number"
    string = "string"
    boolean = "boolean"
    object = "object"


class CustomActionDef(ConfigBaseModel):
    type: CustomActionTypeStr


class CustomActionsIO(ConfigBaseModel):
    inputs: List[CustomActionDef] = []
    outputs: List[CustomActionDef] = []


class AppBaseConfig(ConfigBaseModel):
    name: NameDNS
    title: str
    description: str
    type: AppTypes
    version: VersionStr
    category: Optional[str] = None


def read_schema_file(file_path: Path) -> dict:
    if not os.path.exists(file_path):
        raise ConfigError(f"Schema file {file_path} does not exist.")

    try:
        with open(file_path, "r") as file:
            content = file.read()
            if not content.strip():
                return {}
            return json.loads(content)
    except json.JSONDecodeError:
        raise ConfigError(f"Schema file {file_path} contains invalid JSON.")
