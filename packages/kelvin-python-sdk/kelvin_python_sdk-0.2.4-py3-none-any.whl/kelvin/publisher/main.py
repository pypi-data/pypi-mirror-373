from __future__ import annotations

import asyncio
import importlib
import importlib.util
import os
from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable, List, Optional, Type, Union

import click

from kelvin.config.common import AppTypes, ConfigError
from kelvin.config.parser import missing_config_error, parse_config_file

from .csv_publisher import CSVPublisher
from .server import AssetsEntry, PublisherError, PublishServer, parse_assets_csv
from .simulator import Simulator


def coro(f: Callable) -> Any:
    """
    Decorator to allow async click commands.
    """

    @wraps(f)
    def wrapper(*args, **kwargs):  # type: ignore
        return asyncio.run(f(*args, **kwargs))

    return wrapper


@dataclass
class AssetParameterOverride:
    asset: str
    param: str
    value: str


@click.group()
def kelvin_publisher() -> None:
    pass


@kelvin_publisher.command()
@coro
@click.option(
    "--config",
    required=True,
    default="app.yaml",
    type=click.STRING,
    show_default=True,
    help="Path to the app config file",
)
@click.option("--period", default=5, type=click.FLOAT, show_default=True, help="Publish period in seconds")
@click.option("--min", default=0, type=click.FLOAT, show_default=True, help="Minimum value to publish")
@click.option("--max", default=100, type=click.FLOAT, show_default=True, help="Maximum value to publish")
@click.option(
    "--random/--counter", "rand", default=True, show_default=True, help="Publish random values or incremental"
)
@click.option("--asset-count", type=click.INT, help="Number of test assets from 'test-asset-1' to 'test-asset-N'")
@click.option(
    "--asset-parameter",
    type=click.STRING,
    help="Override asset parameters eg --asset-parameters kelvin_closed_loop=true  (Can be set multiple times)",
    multiple=True,
)
async def simulator(
    config: str,
    period: float,
    min: float,
    max: float,
    rand: bool,
    asset_count: Optional[int],
    asset_parameter: List[str],
) -> None:
    """Generates random data to application's inputs"""
    try:
        app_config = parse_config_file(config)
    except ConfigError as ce:
        if str(ce) == missing_config_error(config):
            print(
                f"Error: Unable to locate the application configuration file. {config}\n"
                "Please make sure you are in the application directory or specify the path using the --config option."
            )
        else:
            print(f"Error: {ce}")
        return

    if app_config.type in [AppTypes.docker, AppTypes.legacy_docker]:
        print(f"Error: simulator is not supported for {app_config.type} applications")
        return

    asset_param_override: List[AssetParameterOverride] = []

    if asset_count is None:
        asset_count = 1
    assets_extra = [AssetsEntry(name=f"test-asset-{i+1}") for i in range(asset_count)]
    for p in asset_parameter:
        param, value = p.split("=", 1)
        asset_param_override.append(AssetParameterOverride(asset="", param=param, value=value))

    gen = Simulator(
        app_config.config, period=period, rand_min=min, rand_max=max, random=rand, assets_extra=assets_extra
    )
    pub = PublishServer(app_config, generator=gen)

    if assets_extra:
        pub.add_extra_assets(assets_extra=assets_extra)

    for param_override in asset_param_override:
        pub.update_param(asset=param_override.asset, param=param_override.param, value=param_override.value)

    await pub.start_server()


class ClickUnion(click.ParamType):
    name = '"csv"|float'

    def __init__(self, types) -> None:  # type: ignore
        self.types = types

    def convert(self, value, param, ctx):  # type: ignore
        for type in self.types:
            try:
                return type.convert(value, param, ctx)
            except click.BadParameter:
                continue

        self.fail("Didn't match any of the accepted types.")


@kelvin_publisher.command()
@coro
@click.option(
    "--config",
    required=True,
    default="app.yaml",
    type=click.STRING,
    show_default=True,
    help="Path to the app config file",
)
@click.option("--csv", required=True, type=click.Path(exists=True), help="Path to the csv file to publish")
@click.option(
    "--publish-interval",
    required=False,
    type=ClickUnion([click.FLOAT, click.STRING]),
    default="csv",
    show_default=True,
    help='Publish interval. Set either to "csv" to use the interval between csv rows or to a number to set a \
fixed publishing interval in seconds.',
)
@click.option(
    "--ignore-timestamps",
    is_flag=True,
    default=False,
    show_default=True,
    help="Ignore CSV timestamps.",
)
@click.option(
    "--now-offset",
    is_flag=True,
    default=False,
    show_default=True,
    help="Offsets the (first) CSV timestamp to current time (now).",
)
@click.option(
    "--replay",
    is_flag=True,
    default=False,
    show_default=True,
    help="Replay mode: Continuously publish data from CSV, restarting from the beginning at end of file",
)
@click.option(
    "--asset-count",
    type=click.INT,
    help="Overrides CSV asset column and generates test assets: from 'test-asset-1' to 'test-asset-N'.",
)
@click.option("--assets", type=click.Path(exists=True), help="Assets Info (Properties) CSV file.")
@click.option(
    "--asset-parameter",
    type=click.STRING,
    help="Override asset parameters eg --asset-parameters kelvin_closed_loop=true  (Can be set multiple times)",
    multiple=True,
)
async def csv(
    config: str,
    csv: str,
    publish_interval: Union[str, float],
    ignore_timestamps: bool,
    now_offset: bool,
    replay: bool,
    asset_count: Optional[int],
    assets: Optional[str],
    asset_parameter: List[str],
) -> None:
    """Publishes data from a csv to the application.
    The publishing rate is determined by the difference between timestamps in the csv rows.
    """
    try:
        app_config = parse_config_file(config)
    except FileNotFoundError:
        print(
            f"Error: Unable to locate the application configuration file. config={config}\n"
            "Please make sure you are in the application directory or specify the path using the --config option."
        )
        return

    if asset_count is not None and app_config.type == AppTypes.bridge:
        print("Error: asset-count is not supported for bridge applications")
        return

    if asset_count is not None and assets is not None:
        print("Error: asset-count and assets cannot be used together")
        return

    if app_config.type in [AppTypes.docker, AppTypes.legacy_docker]:
        print(f"Error: csv is not supported for {app_config.type} applications")
        return

    assets_extra: List[AssetsEntry] = []
    asset_param_override: List[AssetParameterOverride] = []
    if assets:
        csv_assets = parse_assets_csv(assets)
        assets_extra = csv_assets
        for asset in csv_assets:
            for p, v in asset.parameters.items():
                asset_param_override.append(AssetParameterOverride(asset=asset.name, param=p, value=v))
    else:
        if asset_count is None:
            asset_count = 1
        assets_extra = [AssetsEntry(name=f"test-asset-{i+1}") for i in range(asset_count)]

    for p in asset_parameter:
        param, value = p.split("=", 1)
        asset_param_override.append(AssetParameterOverride(asset="", param=param, value=value))

    interval = 0.0
    playback = False
    if publish_interval == "csv":
        playback = True
    else:
        try:
            interval = float(publish_interval)
        except ValueError:
            print("Error: Invalid value for publish-interval. Must be a number or 'csv'")
            return

    try:
        gen = CSVPublisher(csv, interval, playback, ignore_timestamps, now_offset)
        pub = PublishServer(app_config, generator=gen, replay=replay)

        if assets_extra:
            pub.add_extra_assets(assets_extra=assets_extra)

        for param_override in asset_param_override:
            pub.update_param(asset=param_override.asset, param=param_override.param, value=param_override.value)

        await pub.start_server()
    except PublisherError as e:
        print(f"Error: {e}")


def load_class(entry_point: str) -> Type:
    """
    Load a class from a module or file path in the format 'module:ClassName'
    """
    if ":" not in entry_point:
        raise ImportError("Entry point must be in the format 'module:ClassName'")

    module_path, class_name = entry_point.split(":")

    if os.path.exists(module_path):  # It's a file path
        spec = importlib.util.spec_from_file_location("custom_module", module_path)
        module = importlib.util.module_from_spec(spec)  # type: ignore
        spec.loader.exec_module(module)  # type: ignore
    else:  # It's a module name
        module = importlib.import_module(module_path)

    # Get the class from the module
    if not hasattr(module, class_name):
        raise ImportError(f"Class {class_name} not found in module {module_path}.")

    return getattr(module, class_name)


@kelvin_publisher.command()
@coro
@click.option(
    "--config",
    required=True,
    default="app.yaml",
    type=click.STRING,
    show_default=True,
    help="Path to the app config file",
)
@click.option(
    "--entrypoint",
    required=True,
    type=click.STRING,
    help="Path to the entrypoint (setuptools style) of the generator python class. \
It can be path a .py file or path to a module. Eg: mygenerator.py:MyGenerator",
)
@click.option("--asset-count", type=click.INT, help="Number of test assets from 'test-asset-1' to 'test-asset-N'")
async def generator(
    config: str,
    entrypoint: str,
    asset_count: Optional[int],
) -> None:
    """Publishes data generated by a custom generator class"""
    try:
        app_config = parse_config_file(config)
    except FileNotFoundError:
        print(
            f"Error: Unable to locate the application configuration file. config={config}\n"
            "Please make sure you are in the application directory or specify the path using the --config option."
        )
        return

    if asset_count is not None and app_config.type == AppTypes.bridge:
        print("Error: asset-count is not supported for bridge applications")
        return

    asset_count = asset_count or 1
    assets_extra = [AssetsEntry(name=f"test-asset-{i+1}") for i in range(asset_count)]
    try:
        generator_class = load_class(entrypoint)
    except ImportError as e:
        print(f"Error loading generator class: {e!r}")
        return

    gen = generator_class()
    pub = PublishServer(app_config, generator=gen)

    if assets_extra:
        pub.add_extra_assets(assets_extra=assets_extra)

    await pub.start_server()


def main() -> None:
    try:
        asyncio.run(kelvin_publisher())
    except KeyboardInterrupt:
        print("Shutdown.")


if __name__ == "__main__":
    main()
