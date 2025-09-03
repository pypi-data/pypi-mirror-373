#
#  Copyright (c) 2025, NVIDIA CORPORATION. All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an
# express license agreement from NVIDIA CORPORATION is strictly
# prohibited.
#
import json
import os
from io import TextIOWrapper
from threading import Lock
from typing import Any, Optional

from training_telemetry.config import BackendType
from training_telemetry.events import Event, ExceptionEvent
from training_telemetry.internal.backend import Backend
from training_telemetry.internal.backends.record_type import RecordType
from training_telemetry.spans import Span
from training_telemetry.utils import get_logger
from training_telemetry.verbosity import Verbosity

_logger = get_logger(__name__)


class FileBackend(Backend):
    """Backend implementation that writes events and metrics to a file."""

    def __init__(self, filepath: str):
        self._filepath: str = filepath
        self._file: TextIOWrapper | None = self._open_file()
        self._record_count: int = 0
        self._lock: Lock = Lock()
        self.pid = os.getpid()
        self._last_start_span: Optional[Span] = None

    def type(self) -> BackendType:
        return BackendType.FILE

    def verbosity(self) -> Verbosity:
        return Verbosity.INFO

    def _open_file(self) -> TextIOWrapper:
        dir = os.path.dirname(self._filepath)
        if dir:
            os.makedirs(dir, exist_ok=True)
        return open(self._filepath, "w")

    def _write_record(self, record: dict) -> None:
        if not self._file:
            raise RuntimeError("File backend not initialized or already closed")
        with self._lock:
            try:
                self._record_count += 1
                record["count"] = self._record_count
                record["pid"] = self.pid
                json_str = json.dumps(record, separators=(",", ":"))
                self._file.write(json_str + "\n")
                self._file.flush()
            except Exception as e:
                _logger.error(f"Error writing record to file: {e}")

    def _record_span(self, span: Span, record_type: RecordType) -> None:
        record: dict[str, Any] = {
            "type": record_type.value,
            "id": str(span.id),
            "name": span.name.value,
        }
        if record_type == RecordType.START:
            record["event"] = span.start_event.to_json()
        elif record_type == RecordType.COMPLETE:
            assert span.stop_event
            record["elapsed"] = span.duration.elapsed
            record["start_event"] = span.start_event.to_json()
            record["stop_event"] = span.stop_event.to_json()
        elif record_type == RecordType.STOP:
            assert span.stop_event
            record["elapsed"] = span.duration.elapsed
            record["event"] = span.stop_event.to_json()
        else:
            raise ValueError(f"Invalid type: {record_type}")

        self._write_record(record)

    def record_start(self, span: Span) -> None:
        if self._last_start_span is not None:
            self._record_span(self._last_start_span, RecordType.START)
        self._last_start_span = span

    def record_stop(self, span: Span) -> None:
        if span.stop_event is None:
            raise ValueError(f"Span {span.id} has no stop event")
        if self._last_start_span:
            if self._last_start_span.id == span.id:
                # record a complete span rather than two
                self._record_span(span, RecordType.COMPLETE)
                self._last_start_span = None
                return
            else:
                # record the previous span before recording the stop event
                self._record_span(self._last_start_span, RecordType.START)
                self._last_start_span = None

        # record the stop event
        self._record_span(span, RecordType.STOP)

    def record_event(self, event: Event, span: Span) -> None:
        if self._last_start_span:
            self._record_span(self._last_start_span, RecordType.START)
            self._last_start_span = None
        record = {
            "type": RecordType.EVENT.value,
            "id": str(span.id),
            "name": span.name.value,
            "event": event.to_json(),
        }
        self._write_record(record)

    def record_error(self, event: ExceptionEvent, span: Span) -> None:
        if self._last_start_span:
            self._record_span(self._last_start_span, RecordType.START)
            self._last_start_span = None

        record = {
            "type": RecordType.ERROR.value,
            "id": str(span.id),
            "name": span.name.value,
            "event": event.to_json(),
        }
        self._write_record(record)

    def close(self) -> None:
        if self._file is None:
            return
        if self._last_start_span:
            _logger.warning(f"Span {self._last_start_span.id} was not closed")
        with self._lock:
            if self._file is not None:
                self._file.close()
                self._file = None
