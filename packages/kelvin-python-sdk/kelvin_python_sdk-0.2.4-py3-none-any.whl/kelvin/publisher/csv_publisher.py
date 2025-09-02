from __future__ import annotations

import asyncio
import csv
import sys
from datetime import datetime, timedelta
from typing import AsyncGenerator, Optional

import arrow

from kelvin.krn import KRNAssetDataStream
from kelvin.publisher.server import DataGenerator, MessageData, PublisherError


class CSVPublisher(DataGenerator):
    CSV_ASSET_KEY = "asset_name"

    def __init__(
        self,
        csv_file_path: str,
        publish_interval: Optional[float] = None,
        playback: bool = False,
        ignore_timestamps: bool = False,
        now_offset: bool = False,
    ):
        csv.field_size_limit(sys.maxsize)
        self.csv_file_path = csv_file_path
        self.publish_rate = publish_interval
        self.playback = playback
        self.ignore_timestamps = ignore_timestamps
        self.now_offset = now_offset

        csv_file = open(self.csv_file_path)
        csv_reader = csv.reader(csv_file)
        headers = next(csv_reader)

        self.csv_has_timestamp = "timestamp" in headers
        self.use_csv_timestamps = self.csv_has_timestamp and not self.ignore_timestamps

        if self.playback and not self.use_csv_timestamps:
            raise PublisherError("csv must have timestamp column to use publish-interval csv timestamps")

    def parse_timestamp(self, ts_str: str, offset: timedelta = timedelta(0)) -> Optional[datetime]:
        try:
            timestamp = float(ts_str)
            return arrow.get(timestamp).datetime + offset
        except ValueError:
            pass

        try:
            return arrow.get(ts_str).datetime + offset
        except Exception as e:
            print(f"csv: error parsing timestamp. timestamp={ts_str}", e)
            return None

    async def run(self) -> AsyncGenerator[MessageData, None]:
        csv_file = open(self.csv_file_path)
        csv_reader = csv.reader(csv_file)
        headers = next(csv_reader)
        last_timestamp = datetime.max

        ts_offset = timedelta(0)
        row = next(csv_reader)
        row_dict = dict(zip(headers, row))
        timestamp = datetime.now()
        row_ts_str = row_dict.pop("timestamp", "")

        if self.use_csv_timestamps:
            row_ts = self.parse_timestamp(row_ts_str)
            if row_ts is None:
                raise PublisherError(f"csv: invalid timestamp in first row. timestamp={row_ts_str}")

            if self.now_offset:
                ts_offset = timestamp.astimezone() - row_ts.astimezone()

            timestamp = row_ts + ts_offset

        asset = row_dict.pop(self.CSV_ASSET_KEY, "")
        for r, v in row_dict.items():
            if not v:
                continue
            yield MessageData(resource=KRNAssetDataStream(asset, r), value=v, timestamp=timestamp)
        last_timestamp = timestamp
        if self.publish_rate:
            await asyncio.sleep(self.publish_rate)

        for row in csv_reader:
            row_dict = dict(zip(headers, row))
            asset = row_dict.pop(self.CSV_ASSET_KEY, "")

            row_ts_str = row_dict.pop("timestamp", "")
            parsed_ts = self.parse_timestamp(row_ts_str, ts_offset) if self.use_csv_timestamps else datetime.now()
            if parsed_ts is None:
                print("csv: skipping row", row_dict)
                continue
            timestamp = parsed_ts

            if self.playback:
                # wait time between rows
                wait_time = max((timestamp.astimezone() - last_timestamp.astimezone()).total_seconds(), 0)
                last_timestamp = timestamp
                await asyncio.sleep(wait_time)

            for r, v in row_dict.items():
                if not v:
                    continue
                yield MessageData(resource=KRNAssetDataStream(asset, r), value=v, timestamp=timestamp)

            if self.publish_rate:
                await asyncio.sleep(self.publish_rate)

        if self.playback and wait_time > 0:
            # wait same time as last row, before replay
            await asyncio.sleep(wait_time)

        print("\nCSV ingestion is complete")
