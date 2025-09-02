from __future__ import annotations

import asyncio
from asyncio import Event, Queue
from datetime import timedelta
from types import TracebackType
from typing import TYPE_CHECKING, AsyncGenerator, Awaitable, Callable, Dict, List, Optional, Tuple, Type, TypeVar, Union

from pydantic import Field
from pydantic.dataclasses import dataclass
from typing_extensions import Literal, Self, TypeGuard

from kelvin.application import filters
from kelvin.application.stream import KelvinStream, KelvinStreamConfig
from kelvin.krn import KRNAsset, KRNAssetDataStream
from kelvin.logs import configure_logger, logger
from kelvin.message import AssetDataMessage, ControlChangeStatus, KMessageType, KMessageTypeData, Message
from kelvin.message.msg_builders import CustomAction, MessageBuilder, convert_message
from kelvin.message.runtime_manifest import Resource, RuntimeManifest, WayEnum

if TYPE_CHECKING:
    from kelvin.application.window import HoppingWindow, RollingWindow, TumblingWindow

E = TypeVar("E", bound=Exception)
T = TypeVar("T", bound=Message)


@dataclass
class Datastream:
    name: str
    type: KMessageType
    unit: Optional[str] = None


class AppIO(Datastream):
    pass


@dataclass
class ResourceDatastream:
    asset: KRNAsset
    io_name: str
    datastream: Datastream
    configuration: Dict = Field(default_factory=dict)
    way: WayEnum = WayEnum.output

    # deprecated
    owned: bool = False
    access: Literal["RO", "RW", "WO"] = "RO"


@dataclass
class AssetInfo:
    name: str
    properties: Dict[str, Union[bool, float, str]] = Field(default_factory=dict)
    parameters: Dict[str, Union[bool, float, str]] = Field(default_factory=dict)
    datastreams: Dict[str, ResourceDatastream] = Field(default_factory=dict)


class KelvinApp:
    """Kelvin Client to connect to the Application Stream.
    Use this class to connect and interface with the Kelvin Stream.

    After connecting, the connection is handled automatically in the background.

    Use filters or filter_stream to easily listen for specific messages.
    Use register_callback methods to register callbacks for events like connect and disconnect.
    """

    READ_CYCLE_TIMEOUT_S = 0.25
    RECONNECT_TIMEOUT_S = 3

    def __init__(self, config: KelvinStreamConfig = KelvinStreamConfig()) -> None:
        self._stream = KelvinStream(config)
        self._filters: List[Tuple[Queue, Callable[[Message], TypeGuard[Message]]]] = []
        self._conn_task: Optional[asyncio.Task] = None
        self._is_to_connect = False
        self._last_app_config: dict = {}
        self._last_asset_resources: Dict[str, Resource] = {}

        # map of asset name to map of parameter name to parameter message
        self._assets: Dict[str, AssetInfo] = {}
        # dict with the same structure as the configuration defined by the app
        self._app_configuration: dict = {}

        self._runtime_manifest: Optional[RuntimeManifest] = None

        self.on_connect: Optional[Callable[[], Awaitable[None]]] = None
        """ Callback when the connection is established. """
        self.on_disconnect: Optional[Callable[[], Awaitable[None]]] = None
        """ Callback when the connection is closed. """

        self.on_message: Optional[Callable[[Message], Awaitable[None]]] = None
        """ Callback hen a message is received, any message. """
        self.on_asset_input: Optional[Callable[[AssetDataMessage], Awaitable[None]]] = None
        """ Callback when an asset data message is received. """
        self.on_control_change: Optional[Callable[[AssetDataMessage], Awaitable[None]]] = None
        """ Callback when a control change is received. """
        self.on_control_status: Optional[Callable[[ControlChangeStatus], Awaitable[None]]] = None
        """ Callback when a control status is received. """
        self.on_custom_action: Optional[Callable[[CustomAction], Awaitable[None]]] = None
        """ Callback when a custom action is received. """

        self.on_asset_change: Optional[Callable[[Optional[AssetInfo], Optional[AssetInfo]], Awaitable[None]]] = None
        """ Callback when an asset is added, removed or changed.
            First argument is the changed asset (None if it was removed),
        second argument is the previous asset if it was changed. """
        self.on_app_configuration: Optional[Callable[[dict], Awaitable[None]]] = None
        """ Callback when the app configuration is changed. """

        self._config_received = Event()

        self._inputs: List[AppIO] = []
        self._outputs: List[AppIO] = []

        configure_logger()

    async def connect(self) -> None:
        """Establishes a connection to Kelvin Stream.

        This method will wait until the connection is successfully established, and the application is ready to run
        with its initial configuration. If you prefer not to block and want the application to continue execution,
        consider using asyncio.wait_for() with a timeout.
        """
        self._is_to_connect = True
        self._conn_task = asyncio.create_task(self._handle_connection())
        await self.config_received.wait()

    async def disconnect(self) -> None:
        """Disconnects from Kelvin Stream"""
        self._is_to_connect = False
        if self._conn_task:
            await self._conn_task
        await self._stream.disconnect()

    @property
    def assets(self) -> Dict[str, AssetInfo]:
        """Assets
        A dict containing the parameters of each asset configured to this application.
        This dict is automatically updated when the application receives parameter updates.
        eg:
        {
            "asset1": AssetInfo(
                name="asset1",
                properties={
                    "tubing_length": 25.0,
                    "area": 11.0
                },
                parameters={
                    "param-bool": False,
                    "param-number": 7.5,
                    "param-string": "hello",
                },
                datastreams={
                    "output1": ResourceDatastream(
                        asset=KRNAsset("asset1"),
                        io_name="output1",
                        datastream=Datastream(
                            name="datastream1",
                            type=KMessageTypeData("float"),
                            unit="m"
                        ),
                        way=WayEnum.output,
                        access="RO",
                        owned=True,
                        configuration={}
                    )
                }
            )
        }

        Returns:
            Dict[str, AssetInfo]: the dict of the asset parameters
        """

        return self._assets.copy()

    @property
    def app_configuration(self) -> dict:
        """App configuration
        A dict containing the app parameters with the same structure defined in the app.yaml
        eg:
        {
            "foo": {
                "conf_string": "value1",
                "conf_number": 25,
                "conf_bool": False,
            }
        }
        Returns:
            dict: the dict with the app configuration
        """
        return self._app_configuration

    @property
    def config_received(self) -> Event:
        """An asyncio Event that is set when the application receives it's initial configuration
        When the application connects it receives a initial configuration to set the initial app and asset parameters.
        If the application really depends on them this event can be waited (await cli.config_received.wait()) to make
        sure the configuration is available before continuing.

        Returns:
            Event: an awaitable asyncio.Event for the initial app configuration
        """
        return self._config_received

    @property
    def inputs(self) -> List[AppIO]:
        """List of all inputs configured to the application

        class AppIO():
            name: str
            data_type: str

        Returns:
            List[AppIO]: list of input metrics
        """
        return self._inputs

    @property
    def outputs(self) -> List[AppIO]:
        """List of all output configured to the application

        class AppIO():
            name: str
            data_type: str

        Returns:
            List[AppIO]: list of output metrics
        """
        return self._outputs

    async def __aenter__(self) -> Self:
        """Enter the connection."""

        await self.connect()

        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[E]],
        exc_value: Optional[E],
        tb: Optional[TracebackType],
    ) -> Optional[bool]:
        """Exit the connection."""

        try:
            await self.disconnect()
        except Exception:
            pass

        return None

    async def _handle_connection(self) -> None:
        while self._is_to_connect:
            try:
                try:
                    await self._stream.connect()
                except ConnectionError:
                    logger.error(f"Error connecting, reconnecting in {self.RECONNECT_TIMEOUT_S} sec.")
                    await asyncio.sleep(self.RECONNECT_TIMEOUT_S)
                    continue

                if self.on_connect is not None:
                    await self.on_connect()

                await self._handle_read()

                if self.on_disconnect is not None:
                    await self.on_disconnect()
            except Exception:
                logger.exception("Unexpected error on connection handler")
                await asyncio.sleep(self.RECONNECT_TIMEOUT_S)

    async def _handle_read(self) -> None:
        while self._is_to_connect:
            try:
                msg = await self._stream.read()
            except ConnectionError:
                logger.exception("Connection error")
                break

            await self._process_message(msg)

            self._route_to_filters(msg)

    def msg_is_control_change(self, msg: Message) -> TypeGuard[AssetDataMessage]:
        if not isinstance(msg.resource, KRNAssetDataStream) or not isinstance(msg.type, KMessageTypeData):
            return False

        try:
            resource = self.assets[msg.resource.asset].datastreams[msg.resource.data_stream]
        except KeyError:
            return False

        return resource.way in [WayEnum.input_cc_output, WayEnum.input_cc]

    async def _process_runtime_manifest(self, msg: RuntimeManifest) -> None:
        self._runtime_manifest = msg
        self._app_configuration = msg.payload.configuration
        if self.app_configuration != self._last_app_config:
            self._last_app_config = self.app_configuration
            if self.on_app_configuration is not None and self._config_received.is_set():
                await self.on_app_configuration(self.app_configuration)

        inputs = {}
        outputs = {}
        assets_in_manifest = set()
        for resource in msg.payload.resources:
            # check resource is asset
            if not isinstance(resource.resource, KRNAsset):
                continue

            asset_name = resource.resource.asset

            assets_in_manifest.add(asset_name)

            self._last_asset_resources[asset_name] = resource
            asset_info = AssetInfo(
                name=asset_name, properties=resource.properties, parameters=resource.parameters, datastreams={}
            )

            for ds_name, datastream in resource.datastreams.items():
                manif_ds = next((ds for ds in msg.payload.datastreams if ds.name == ds_name), None)
                if manif_ds is None:
                    continue

                name = datastream.map_to if datastream.map_to else ds_name
                asset_info.datastreams[name] = ResourceDatastream(
                    asset=resource.resource,
                    io_name=name,
                    access=datastream.access,
                    way=datastream.way,
                    owned=datastream.owned or False,
                    configuration=datastream.configuration,
                    datastream=Datastream(
                        name=ds_name,
                        type=KMessageTypeData(manif_ds.primitive_type_name),  # type: ignore
                        unit=manif_ds.unit_name,
                    ),
                )

                if datastream.way in [WayEnum.input, WayEnum.input_output_cc]:
                    inputs[name] = AppIO(name=name, type=KMessageTypeData(manif_ds.primitive_type_name))  # type: ignore
                elif datastream.way in [WayEnum.output, WayEnum.input_cc_output]:
                    outputs[name] = AppIO(
                        name=name, type=KMessageTypeData(manif_ds.primitive_type_name)  # type: ignore
                    )

            old_asset_info = self._assets.get(asset_name, None)
            self._assets[asset_name] = asset_info

            if self.on_asset_change is not None and self._config_received.is_set():
                await self.on_asset_change(asset_info, old_asset_info)

        self._inputs = list(inputs.values())
        self._outputs = list(outputs.values())

        # check for removed assets
        for asset_name in set(self._assets.keys()) - assets_in_manifest:
            old_asset_info = self._assets.pop(asset_name, None)
            self._last_asset_resources.pop(asset_name, None)
            if self.on_asset_change is not None and self._config_received.is_set() and old_asset_info:
                await self.on_asset_change(None, old_asset_info)

    async def _process_message(self, msg: Message) -> None:
        if isinstance(msg, RuntimeManifest):
            await self._process_runtime_manifest(msg)
            self._config_received.set()

        if self.on_message is not None:
            await self.on_message(msg)

        if self.on_control_change is not None and self.msg_is_control_change(msg):
            await self.on_control_change(msg)  # type: ignore
            return

        if self.on_asset_input is not None and filters.is_asset_data_message(msg):
            await self.on_asset_input(msg)  # type: ignore
            return

        if self.on_control_status is not None and filters.is_control_status_message(msg):
            await self.on_control_status(msg)  # type: ignore
            return

        if self.on_custom_action is not None and filters.is_custom_action(msg):
            converted = convert_message(msg)  # type: ignore
            await self.on_custom_action(converted)  # type: ignore
            return

    def _route_to_filters(self, msg: Message) -> None:
        for queue, func in self._filters:
            if func(msg) is True:
                converted = convert_message(msg) or msg  # convert to message builder
                # todo: check if the message is reference
                queue.put_nowait(converted)

    def filter(self, func: Callable[[Message], TypeGuard[T]]) -> Queue[T]:
        """Creates a filter for the received Kelvin Messages based on a filter function.

        Args:
            func (filters.KelvinFilterType): Filter function, it should receive a Message as argument and return bool.

        Returns:
            Queue[Message]: Returns a asyncio queue to receive the filtered messages.
        """
        queue: Queue[T] = Queue()
        self._filters.append((queue, func))
        return queue

    def stream_filter(self, func: Callable[[Message], TypeGuard[T]]) -> AsyncGenerator[T, None]:
        """Creates a stream for the received Kelvin Messages based on a filter function.
        See filter.

        Args:
            func (filters.KelvinFilterType): Filter function, it should receive a Message as argument and return bool.

        Returns:
            AsyncGenerator[Message, None]: Async Generator that can be async iterated to receive filtered messages.

        Yields:
            Iterator[AsyncGenerator[Message, None]]: Yields the filtered messages.
        """
        queue: Queue[T] = self.filter(func)

        async def _generator() -> AsyncGenerator[T, None]:
            while True:
                msg = await queue.get()
                yield msg

        return _generator()

    def tumbling_window(
        self,
        window_size: timedelta,
        assets: Optional[List[str]] = None,
        datastreams: Optional[List[str]] = None,
        round_to: Optional[timedelta] = None,
    ) -> TumblingWindow:

        from kelvin.application.window import TumblingWindow

        if not assets:
            assets = list(self.assets.keys())

        if not datastreams:
            datastreams = [ds.name for ds in self.inputs]

        # Subscribe to asset/datastreams
        def _checker(msg: Message) -> TypeGuard[AssetDataMessage]:
            asset_func = filters.asset_equals(assets)
            input_func = filters.input_equals(datastreams)
            return asset_func(msg) and input_func(msg)

        queue = self.filter(_checker)

        return TumblingWindow(
            assets=assets, datastreams=datastreams, window_size=window_size, queue=queue, round_to=round_to
        )

    def hopping_window(
        self,
        window_size: timedelta,
        hop_size: timedelta,
        assets: Optional[List[str]] = None,
        datastreams: Optional[List[str]] = None,
        round_to: Optional[timedelta] = None,
    ) -> HoppingWindow:

        from kelvin.application.window import HoppingWindow

        if not assets:
            assets = list(self.assets.keys())

        if not datastreams:
            datastreams = [ds.name for ds in self.inputs]

        # Subscribe to asset/datastreams
        def _checker(msg: Message) -> TypeGuard[AssetDataMessage]:
            asset_func = filters.asset_equals(assets)
            input_func = filters.input_equals(datastreams)
            return asset_func(msg) and input_func(msg)

        queue = self.filter(_checker)

        return HoppingWindow(
            assets=assets,
            datastreams=datastreams,
            window_size=window_size,
            hop_size=hop_size,
            queue=queue,
            round_to=round_to,
        )

    def rolling_window(
        self,
        count_size: int,
        assets: Optional[List[str]] = None,
        datastreams: Optional[List[str]] = None,
        round_to: Optional[timedelta] = None,
    ) -> RollingWindow:

        from kelvin.application.window import RollingWindow

        if not assets:
            assets = list(self.assets.keys())

        if not datastreams:
            datastreams = [ds.name for ds in self.inputs]

        # Subscribe to asset/datastreams
        def _checker(msg: Message) -> TypeGuard[AssetDataMessage]:
            asset_func = filters.asset_equals(assets)
            input_func = filters.input_equals(datastreams)
            return asset_func(msg) and input_func(msg)

        queue = self.filter(_checker)

        return RollingWindow(
            assets=assets, datastreams=datastreams, count_size=count_size, queue=queue, round_to=round_to
        )

    async def publish(self, msg: Union[Message, MessageBuilder]) -> bool:
        """Publishes a Message to Kelvin Stream

        Args:
            msg (Message): Kelvin Message to publish

        Returns:
            bool: True if the message was sent with success.
        """
        try:
            if isinstance(msg, MessageBuilder):
                m = msg.to_message()
            else:
                m = msg

            return await self._stream.write(m)
        except ConnectionError:
            logger.error("Failed to publish message, connection is unavailable.")
            return False
