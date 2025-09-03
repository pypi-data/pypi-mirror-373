from __future__ import annotations

import struct
import uuid as _uuid
# (no external IO types needed)


def encode_uint8(value: int) -> bytes:
    return struct.pack("<B", value)


def encode_uint16(value: int) -> bytes:
    return struct.pack("<H", value)


def encode_string(value: str) -> bytes:
    data = value.encode("utf-8")
    return encode_uint16(len(data)) + data


def encode_uuid(value: _uuid.UUID) -> bytes:
    return value.bytes
