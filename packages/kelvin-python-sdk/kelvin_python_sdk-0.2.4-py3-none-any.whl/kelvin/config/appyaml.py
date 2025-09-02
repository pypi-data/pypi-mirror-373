from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel

from .common import AppTypes, ConfigBaseModel
from .manifest import AppManifest


class ConfigurationError(Exception):
    pass


class MetricInfo(BaseModel):
    model_config = {"extra": "allow"}

    asset_names: Optional[List[str]] = []


class Metric(BaseModel):
    model_config = {"extra": "allow"}

    name: str
    data_type: str
    control_change: bool = False


class ParameterDefinition(BaseModel):
    model_config = {"extra": "allow"}

    name: str
    data_type: str
    default: Optional[Dict] = None


class MetricInput(Metric):
    model_config = {"extra": "allow"}

    sources: Optional[List[MetricInfo]] = []


class MetricOutput(Metric):
    model_config = {"extra": "allow"}

    targets: Optional[List[MetricInfo]] = []


class AssetsEntry(BaseModel):
    model_config = {"extra": "allow"}

    name: str
    parameters: Dict[str, Any] = {}
    properties: Dict[str, Any] = {}


class MetricMap(BaseModel):
    model_config = {"extra": "allow"}

    name: str
    asset_name: str
    data_type: str
    access: str = "RO"
    configuration: Dict = {}


class AppKelvin(BaseModel):
    model_config = {"extra": "allow"}

    assets: List[AssetsEntry] = []
    inputs: List[Metric] = []
    outputs: List[Metric] = []
    parameters: List[ParameterDefinition] = []
    configuration: Dict = {}


class AppBridge(BaseModel):
    model_config = {"extra": "allow"}

    metrics_map: List[MetricMap] = []
    configuration: Dict = {}


class AppDocker(ConfigBaseModel):
    model_config = {"extra": "allow"}


class EnvironmentConfig(ConfigBaseModel):
    workload_name: str
    node_name: str


class AppConfig(ConfigBaseModel):
    type: Literal[AppTypes.bridge, AppTypes.kelvin_app, AppTypes.docker]
    kelvin: Optional[AppKelvin] = None
    bridge: Optional[AppBridge] = None
    docker: Optional[AppDocker] = None


class AppYamlInfo(ConfigBaseModel):
    name: str
    title: str
    description: str
    version: str


class SystemConfig(ConfigBaseModel):
    model_config = {"extra": "allow"}
    privileged: bool = False


class AppYaml(ConfigBaseModel):
    spec_version: str
    environment: Optional[EnvironmentConfig] = None
    info: AppYamlInfo
    app: AppConfig
    system: Optional[SystemConfig] = None

    def to_manifest(self, read_schemas: bool = True, workdir: Path = Path(".")) -> AppManifest:
        return AppManifest(
            name=self.info.name,
            title=self.info.title,
            description=self.info.description,
            version=self.info.version,
            type=self.app.type,
            spec_version=self.spec_version,
        )
