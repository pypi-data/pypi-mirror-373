from __future__ import annotations

import asyncio
import random
from typing import AsyncGenerator, Dict, List, Union

from kelvin.application.config import ConfigurationError
from kelvin.config.appyaml import (
    AppYaml,
    AssetsEntry,
)
from kelvin.config.common import AppTypes
from kelvin.config.exporter import ExporterConfig
from kelvin.config.external import ExternalConfig
from kelvin.config.importer import ImporterConfig
from kelvin.config.smart_app import SmartAppConfig
from kelvin.krn import KRNAssetDataStream
from kelvin.publisher.server import AppIO, DataGenerator, MessageData


class Simulator(DataGenerator):
    app_yaml: str
    app_config: ExporterConfig | ImporterConfig | SmartAppConfig | ExternalConfig | AppYaml
    rand_min: float
    rand_max: float
    random: bool
    current_value: float
    assets: List[AssetsEntry]
    params_override: Dict[str, Union[bool, float, str]]

    def __init__(
        self,
        app_config: ExporterConfig | ImporterConfig | SmartAppConfig | ExternalConfig | AppYaml,
        period: float,
        rand_min: float = 0,
        rand_max: float = 100,
        random: bool = True,
        assets_extra: List[AssetsEntry] = [],
        parameters_override: List[str] = [],
    ):
        self.app_config = app_config
        self.period = period
        self.rand_min = rand_min
        self.rand_max = rand_max
        self.random = random
        self.current_value = self.rand_min - 1
        self.params_override: Dict[str, Union[bool, float, str]] = {}

        for override in parameters_override:
            param, value = override.split("=", 1)
            self.params_override[param] = value

        if len(assets_extra) > 0:
            self.assets = assets_extra

    def generate_random_value(self, data_type: str) -> Union[bool, float, str, dict]:
        if data_type == "boolean":
            return random.choice([True, False])

        if self.random:
            number = round(random.random() * (self.rand_max - self.rand_min) + self.rand_min, 2)
        else:
            if self.current_value >= self.rand_max:
                self.current_value = self.rand_min
            else:
                self.current_value += 1
            number = self.current_value

        if data_type == "number":
            return number

        if data_type == "string":
            return f"str_{number}"

        # object or other icd
        return {"key": number}

    async def run(self) -> AsyncGenerator[MessageData, None]:
        app_inputs: List[AppIO] = []
        if (
            isinstance(self.app_config, AppYaml)
            and self.app_config.app.type == AppTypes.kelvin_app
            and self.app_config.app.kelvin is not None
        ):
            for asset in self.assets:
                for app_input in self.app_config.app.kelvin.inputs:
                    app_inputs.append(AppIO(name=app_input.name, data_type=app_input.data_type, asset=asset.name))

        elif (
            isinstance(self.app_config, AppYaml)
            and self.app_config.app.type == AppTypes.bridge
            and self.app_config.app.bridge is not None
        ):
            app_inputs = [
                AppIO(name=metric.name, data_type=metric.data_type, asset=metric.asset_name)
                for metric in self.app_config.app.bridge.metrics_map
                if metric.access == "RW"
            ]

        elif isinstance(self.app_config, SmartAppConfig):
            for asset in self.assets:
                for inpt in self.app_config.data_streams.inputs:
                    app_inputs.append(AppIO(name=inpt.name, data_type=inpt.data_type, asset=asset.name))

                for cc in self.app_config.control_changes.inputs:
                    app_inputs.append(AppIO(name=cc.name, data_type=cc.data_type, asset=asset.name))

        else:
            raise ConfigurationError("invalid app type")

        while True:
            for i in app_inputs:
                yield MessageData(
                    resource=KRNAssetDataStream(i.asset, i.name),
                    value=self.generate_random_value(i.data_type),
                    timestamp=None,
                )

            await asyncio.sleep(self.period)
