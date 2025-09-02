import asyncio
from datetime import datetime, timedelta, timezone
from typing import AsyncGenerator, Dict, List, Optional, Tuple

from kelvin.message import AssetDataMessage

try:
    import pandas as pd
except ImportError as e:
    raise ImportError(
        "Missing requirements to use this feature. Install with `pip install 'kelvin-python-sdk[ai]'`"
    ) from e


UTC = timezone.utc


def round_nearest_time(dt: datetime, round_to: Optional[timedelta] = None) -> datetime:
    """
    Rounds the given datetime to the nearest time interval as specified by self.round_to.

    Args:
        dt (datetime): The datetime to round.

    Returns:
        datetime: The rounded datetime.
    """

    if not round_to:
        return dt  # No rounding if round_to is not set

    # Convert both datetime and timedelta to seconds for easier calculations
    dt_seconds = dt.timestamp()
    round_to_seconds = round_to.total_seconds()

    # Find the nearest time by rounding the timestamp to the nearest multiple of round_to seconds
    rounded_timestamp = round(dt_seconds / round_to_seconds) * round_to_seconds

    # Convert the rounded timestamp back to a datetime object, preserving timezone information
    rounded_dt = datetime.fromtimestamp(rounded_timestamp, tz=dt.tzinfo)

    return rounded_dt


class BaseWindow:
    """A base class for managing data windows for streaming data."""

    def __init__(
        self, assets: List[str], datastreams: List[str], queue: asyncio.Queue, round_to: Optional[timedelta] = None
    ) -> None:
        """
        Initializes the BaseWindow with the necessary parameters.

        Args:
            assets (List[str]): List of asset identifiers.
            datastreams (List[str]): List of data stream identifiers.
            queue (asyncio.Queue): The queue from which messages are consumed.
            round_to (Optional[timedelta]): The timedelta to which timestamps should be rounded.
        Raises:
            ValueError: If any parameter is invalid.
        """

        # Validate that assets are correctly specified
        if not isinstance(assets, list) or not all(isinstance(asset, str) and asset for asset in assets):
            raise ValueError("assets must be a list of non-empty strings")

        # Validate that datastreams are correctly specified
        if not isinstance(datastreams, list) or not all(
            isinstance(datastream, str) and datastream.strip() for datastream in datastreams
        ):
            raise ValueError("datastreams must be a list of non-empty strings")

        # Validate that the queue is an asyncio.Queue instance
        if not isinstance(queue, asyncio.Queue):
            raise ValueError("queue must be an asyncio.Queue instance")

        # Validate the round_to parameter if provided
        if round_to is not None and (not isinstance(round_to, timedelta) or round_to <= timedelta()):
            raise ValueError("round_to must be a positive timedelta instance or None")

        self.queue = queue
        self.assets = assets
        self.datastreams = datastreams
        self.round_to = round_to
        self.dataframes: Dict[str, pd.DataFrame] = self._initialize_dataframes()

    def _initialize_dataframes(self) -> Dict[str, pd.DataFrame]:
        """
        Initializes the dataframes for the specified assets and datastreams.
        """
        return {
            asset: pd.DataFrame(columns=self.datastreams, index=pd.DatetimeIndex([], name="timestamp", tz=UTC))
            for asset in self.assets
        }

    def _append(self, message: AssetDataMessage, window_start: Optional[datetime] = None) -> None:
        """
        Appends a message to the appropriate DataFrame.

        Args:
            message (AssetDataMessage): The message to append.
            window_start (Optional[datetime]): The start time of the window to check against.
                If supplied, it must be timezone-aware.
        """
        asset = message.resource.asset
        datastream = message.resource.data_stream
        value = message.payload
        timestamp = round_nearest_time(message.timestamp, self.round_to)
        timestamp = timestamp.astimezone(UTC)  # Ensure timestamp is in UTC

        if window_start is not None:
            window_start = window_start.astimezone(UTC)

        if asset not in self.assets:
            # Ignore messages for assets not in the list
            print(f"Dropping message for asset not in the list. Asset: {asset}")
            return

        if datastream not in self.datastreams:
            # Ignore messages for datastreams not in the list
            print(f"Dropping message for datastream not in the list. Asset:{asset}. DataStream: {datastream}")
            return

        if window_start and timestamp < window_start:
            # Ignore messages before the window start
            print(
                f"Dropping message before window start."
                f" Asset: {asset}. DataStream: {datastream}. Timestamp: {timestamp}"
            )
            return

        # Insert the new data into the DataFrame
        self.dataframes[asset].at[timestamp, datastream] = value

    def get_df(self, asset_name: str) -> pd.DataFrame:
        """
        Returns the DataFrame for the specified asset.

        Args:
            asset_name (str): The asset name identifier.

        Returns:
            Optional[pd.DataFrame]: The DataFrame for the asset if available, None otherwise.
        """
        return self.dataframes.get(asset_name, None)


class BaseTimeWindow(BaseWindow):
    """A base class for time-based windowing of data streams."""

    def __init__(
        self,
        assets: List[str],
        datastreams: List[str],
        queue: asyncio.Queue,
        window_size: timedelta,
        hop_size: timedelta,
        round_to: Optional[timedelta] = None,
    ) -> None:
        """
        Initializes a time-based window with the provided parameters.

        Args:
            assets (List[str]): List of asset identifiers.
            datastreams (List[str]): List of data stream identifiers.
            queue (asyncio.Queue): The queue from which messages are consumed.
            window_size (timedelta): The duration of each window.
            hop_size (timedelta): The time between the starts of consecutive windows.
            round_to (Optional[timedelta]): The timedelta to which timestamps should be rounded.
        Raises:
            ValueError: If window_size or hop_size is not a positive timedelta.
        """
        super().__init__(assets=assets, datastreams=datastreams, queue=queue, round_to=round_to)

        if not isinstance(window_size, timedelta) or window_size <= timedelta():
            raise ValueError("window_size must be a positive timedelta")
        if not isinstance(hop_size, timedelta) or hop_size <= timedelta():
            raise ValueError("hop_size must be a positive timedelta")

        self.window_size = window_size
        self.hop_size = hop_size

    async def _consume(self, timeout: float) -> Optional[AssetDataMessage]:
        """
        Attempts to consume a message from the queue within the specified timeout.

        Args:
            timeout (float): The timeout in seconds.

        Returns:
            Optional[Message]: The message if available, None otherwise.
        """
        try:
            return await asyncio.wait_for(self.queue.get(), timeout=timeout)
        except asyncio.TimeoutError:
            return None

    async def stream(self, window_start: Optional[datetime] = None) -> AsyncGenerator[Tuple[str, pd.DataFrame], None]:
        """
        Streams data windows continuously by consuming messages and yielding appropriate windows.

        Args:
            window_start (Optional[datetime]): The start time of the window. Defaults to the current time.
                If provided, it must be timezone-aware.

        Yields:
            AsyncGenerator[Tuple[str, pd.DataFrame], None]: Generator yielding asset and its respective DataFrame.
        """
        window_start = datetime.now(UTC) if window_start is None else window_start.astimezone(UTC)
        window_end = window_start + self.hop_size

        while True:
            remaining_time = (window_end - datetime.now(UTC)).total_seconds()
            if remaining_time <= 0:
                for asset, df in self.dataframes.items():
                    df.sort_index(inplace=True)  # Sort to ensure chronological order

                    window_df = df[(df.index >= window_start) & (df.index < window_start + self.window_size)]

                    yield asset, window_df
                    df.drop(df[df.index < window_end].index, inplace=True)  # Clean up data outside of the window

                window_start = window_end
                window_end = window_start + self.hop_size
                continue

            msg = await self._consume(timeout=remaining_time)
            if msg:
                self._append(message=msg)


class TumblingWindow(BaseTimeWindow):
    """A class representing tumbling time windows where each window is discrete and non-overlapping."""

    def __init__(
        self,
        assets: List[str],
        datastreams: List[str],
        queue: asyncio.Queue,
        window_size: timedelta,
        round_to: Optional[timedelta] = None,
    ) -> None:
        """
        Initializes a TumblingWindow with the same size for window and hop size.

        Args:
            assets (List[str]): List of asset identifiers.
            datastreams (List[str]): List of data stream identifiers.
            queue (asyncio.Queue): The queue from which messages are consumed.
            window_size (timedelta): The duration of each window.
            round_to (Optional[timedelta]): The timedelta to which timestamps should be rounded.
        """
        super().__init__(
            assets=assets,
            datastreams=datastreams,
            queue=queue,
            window_size=window_size,
            hop_size=window_size,
            round_to=round_to,
        )


class HoppingWindow(BaseTimeWindow):
    """
    A class for hopping windows where windows may overlap depending on the hop size being smaller than the window size.
    """

    def __init__(
        self,
        assets: List[str],
        datastreams: List[str],
        queue: asyncio.Queue,
        window_size: timedelta,
        hop_size: timedelta,
        round_to: Optional[timedelta] = None,
    ) -> None:
        """
        Initializes a HoppingWindow with distinct window and hop sizes.

        Args:
            assets (List[str]): List of asset identifiers.
            datastreams (List[str]): List of data stream identifiers.
            queue (asyncio.Queue): The queue from which messages are consumed.
            window_size (timedelta): The duration of each window.
            hop_size (timedelta): The time between the starts of consecutive windows.
            round_to (Optional[timedelta]): The timedelta to which timestamps should be rounded.
        """
        super().__init__(
            assets=assets,
            datastreams=datastreams,
            queue=queue,
            window_size=window_size,
            hop_size=hop_size,
            round_to=round_to,
        )


class RollingWindow(BaseWindow):
    """A class for rolling windows based on a count of messages rather than time."""

    def __init__(
        self,
        assets: List[str],
        datastreams: List[str],
        queue: asyncio.Queue,
        count_size: int,
        round_to: Optional[timedelta] = None,
    ):
        """
        Initializes a RollingWindow based on a fixed count of messages.

        Args:
            assets (List[str]): List of asset identifiers.
            datastreams (List[str]): List of data stream identifiers.
            queue (asyncio.Queue): The queue from which messages are consumed.
            count_size (int): The number of messages in each window.
            round_to (Optional[timedelta]): The timedelta to which timestamps should be rounded.
        Raises:
            ValueError: If count_size is not a positive integer.
        """
        super().__init__(assets=assets, datastreams=datastreams, queue=queue, round_to=round_to)
        if count_size <= 0:
            raise ValueError("count_size must be a positive integer")
        self.count_size = count_size

    async def stream(self) -> AsyncGenerator[Tuple[str, pd.DataFrame], None]:
        """
        Streams data windows continuously by consuming messages and yielding windows based on the count of messages.

        Yields:
            AsyncGenerator[Tuple[str, pd.DataFrame], None]: Generator yielding asset and its respective DataFrame.
        """
        window_start = None

        while True:
            msg = await self.queue.get()
            self._append(msg, window_start=window_start)

            asset = msg.resource.asset

            df = self.dataframes.get(asset)
            if df is not None:
                window_start = df.index[0]
                if len(df) >= self.count_size:
                    df.sort_index(inplace=True)

                    if len(df) > self.count_size:
                        df.drop(df.index[0], inplace=True)  # Maintain the window size by dropping the oldest entry

                    yield asset, df.copy()
                    window_start = df.index[0]  # Update window start to manage message order
