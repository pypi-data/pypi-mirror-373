from __future__ import annotations

import uuid as _uuid
from typing import List

from pydantic import BaseModel, Field, field_validator


class WordSegment(BaseModel):
    start_time: float = Field(alias="start_time")
    end_time: float = Field(alias="end_time")
    word: str


class UUID(BaseModel):
    UUID: _uuid.UUID

    @field_validator("UUID", mode="before")
    @classmethod
    def _parse_uuid(cls, v):  # type: ignore[override]
        if isinstance(v, _uuid.UUID):
            return v
        if isinstance(v, dict) and "UUID" in v:
            return _uuid.UUID(v["UUID"])  # pragma: no cover
        return _uuid.UUID(str(v))


class ConnectedResponse(BaseModel):
    id: str


class ErrorResponse(BaseModel):
    id: UUID
    message: str


class FileUploadedResponse(BaseModel):
    id: UUID
    message: str


class _BaseTranscribeResponse(BaseModel):
    id: UUID
    seq: int
    transcription: str
    words: List[WordSegment] = []
    is_final: bool = Field(alias="is_final")

    @field_validator("id", mode="before")
    @classmethod
    def _coerce_id(cls, v):  # type: ignore[override]
        # Accept raw UUID string/uuid.UUID and wrap into our UUID model
        if isinstance(v, UUID):
            return v
        if isinstance(v, (str, _uuid.UUID)):
            return {"UUID": str(v)}
        if isinstance(v, dict):
            return v
        return v


class FtTranscribeResponse(_BaseTranscribeResponse):
    pass


class RtTranscribeResponse(_BaseTranscribeResponse):
    is_speech_final: bool = Field(alias="is_speech_final")
