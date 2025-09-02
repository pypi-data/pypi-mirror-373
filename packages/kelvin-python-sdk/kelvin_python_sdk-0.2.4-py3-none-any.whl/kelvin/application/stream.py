from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from asyncio import StreamReader, StreamWriter
from typing import Optional

from pydantic_settings import BaseSettings

from kelvin.message import Message


class StreamInterface(ABC):
    """Interface for a connection to a Kelvin system. Provides raw read/write access."""

    @abstractmethod
    async def connect(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnects from the Kelvin Stream"""
        raise NotImplementedError

    @abstractmethod
    async def read(self) -> Message:
        raise NotImplementedError

    @abstractmethod
    async def write(self, msg: Message) -> bool:
        raise NotImplementedError


class KelvinStreamConfig(BaseSettings):
    model_config = {"env_prefix": "KELVIN_STREAM_"}

    ip: str = "127.0.0.1"
    port: int = 49167
    limit: int = 2**22


class KelvinStream(StreamInterface):
    _reader: Optional[StreamReader]
    _writer: Optional[StreamWriter]

    def __init__(self, config: KelvinStreamConfig = KelvinStreamConfig()) -> None:
        self._config = config
        self._writer = None
        self._reader = None

    async def connect(self) -> None:
        """Connects to Kelvin Stream

        Raises:
            ConnectionError: If the stream server is unreachable.
        """
        self._reader, self._writer = await asyncio.open_connection(
            self._config.ip, self._config.port, limit=self._config.limit
        )

    async def disconnect(self) -> None:
        """Disconnects from Kelvin Stream"""
        if self._writer:
            self._writer.close()

    async def read(self) -> Message:
        """Reads the next Kelvin Message

        Raises:
            ConnectionError: When connection is unavailable.

        Returns:
            Message: the read Message
        """
        data = await self._reader.readline()  # type: ignore
        if not len(data):
            raise ConnectionError("Connection lost.")

        return Message.model_validate_json(data)

    async def write(self, msg: Message) -> bool:
        """Writes a Message to the Kelvin Stream

        Args:
            msg (Message): Kelvin message to write

        Raises:
            ConnectionError: If the connection is lost.

        Returns:
            bool: True if the message was sent with success.
        """
        if self._writer:
            self._writer.write(msg.encode() + b"\n")
            await self._writer.drain()
            return True

        return False
