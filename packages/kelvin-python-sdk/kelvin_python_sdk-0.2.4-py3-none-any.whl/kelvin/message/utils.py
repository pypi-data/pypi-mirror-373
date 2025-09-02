"""Utility functions."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Iterator, Mapping, Tuple


def flatten(x: Mapping[str, Any], separator: str = ".") -> Iterator[Tuple[str, Any]]:
    """Flatten nested mappings."""

    return (
        (k if not l else f"{k}{separator}{l}", w)
        for k, v in x.items()
        for l, w in (flatten(v) if isinstance(v, Mapping) else [("", v)])  # noqa: E741
    )


def to_rfc3339_timestamp(x: datetime) -> str:
    """Convert datetime to RFC-3339 timestamp (UTC)."""

    suffix = "Z" if x.microsecond else ".000000Z"

    return x.astimezone(timezone.utc).replace(tzinfo=None).isoformat() + suffix


def from_rfc3339_timestamp(x: str) -> datetime:
    """Convert RFC-3339 timestamp to datetime (UTC)."""

    if x.endswith("Z"):
        x = f"{x[:-1]}+00:00"

    return datetime.fromisoformat(x).astimezone()
