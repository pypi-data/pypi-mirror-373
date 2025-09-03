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
import logging
import os
import re
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


class PythonLoggerBackend(Backend):
    """
    Backend implementation that writes spans and events using a python logger.
    Note that this python logger may be backed by an Open Telemetry logger.
    Events are formatted as key=value pairs with hierarchical keys separated by dots.
    """

    def __init__(self, logger: logging.Logger, verbosity: Verbosity):
        self._logger = logger
        self._record_count: int = 0
        self._lock: Lock = Lock()
        self._verbosity: Verbosity = verbosity
        self.pid = os.getpid()
        self._last_start_span: Optional[Span] = None

    def type(self) -> BackendType:
        return BackendType.LOGGER

    def verbosity(self) -> Verbosity:
        return self._verbosity

    def _increment_record_count(self) -> int:
        with self._lock:
            self._record_count += 1
            return self._record_count

    def format_log(self, event_json: dict, prefix: str = "") -> str:
        """
        Format the dictionary into a log string. The output string will be in the format of "[key1=value1 | key2=value2 | ...]".
        Nested dictionaries are formatted recursively, and will be in the format of "key1.key2=value where key1 is the top
        level key and key2 is the nested key in the nested dictionary".

        The prefix argumentindicates if the dictionary is a top-level dictionary or a nested dictionary.
        Top level dictionaries are enclosed in square brackets, and have some additional properties like the process id and
        the record count added to the dictionary.

        Args:
            event_json (dict): The dictionary to format.
            prefix (str): The prefix indicates if the dictionary is a top-level dictionary or a nested dictionary.
                          This function is in fact called recursively to format nested dictionaries, and for nested dictionaries
                          the prefix is the key of the nested dictionary in the parent dictionary.

        Limitations:
            - dictionary keys cannot contain dots.
        Returns:
            str: The formatted log string.
        """
        if not prefix:
            event_json["count"] = self._increment_record_count()
            event_json["pid"] = self.pid
        items: list[str] = []
        for k, v in sorted(event_json.items(), reverse=True):
            if "." in k:
                raise ValueError(f"keys cannot contain dots: {k}")

            if isinstance(v, dict):
                child_prefix = f"{prefix}.{k}" if prefix else k
                items.append(self.format_log(event_json=v, prefix=child_prefix))
            else:
                if prefix:
                    items.append(f"{prefix}.{k}={v}")
                else:
                    items.append(f"{k}={v}")
        if prefix:
            return " | ".join(items)
        else:
            return "[" + " | ".join(items) + "]"

    @staticmethod
    def deserialize_log(text: str) -> dict:
        """
        Unformat a log string back into a dictionary by reversing the format_log function. Refer to that function
        for details on the format of the log string.
        """
        # First extract all the characters that are in the top level square brackets.
        pattern = r"\[(.*?)\]"
        matches = re.findall(pattern, text, re.DOTALL)
        if not matches:
            raise ValueError(f"Log string must be enclosed in square brackets: {text}")

        # Then split the text by the pipe character with a space on each side of the pipe.
        items = matches[-1].split(" | ")  # FIXME - exclude text inside double quotes

        ret: dict[str, Any] = {}
        for item in items:
            k, v = item.split("=")  # FIXME - exclude text inside double quotes
            d = ret
            while "." in k:
                k1, k2 = k.split(".", 1)
                if k1 not in d:
                    d[k1] = {}
                k = k2
                d = d[k1]
            try:
                d[k] = json.loads(v)
            except ValueError as e:
                d[k] = v
        return ret

    def _record_span(self, span: Span, record_type: RecordType) -> None:
        json_dict: dict[str, Any] = {
            "type": record_type.value,
            "name": span.name.value,
        }
        if record_type == RecordType.START:
            json_dict["event"] = span.start_event.to_json()
        elif record_type == RecordType.COMPLETE:
            assert span.stop_event
            json_dict["start_event"] = span.start_event.to_json()
            json_dict["stop_event"] = span.stop_event.to_json()
            json_dict["elapsed"] = span.duration.elapsed
        elif record_type == RecordType.STOP:
            assert span.stop_event
            json_dict["event"] = span.stop_event.to_json()
            json_dict["elapsed"] = span.duration.elapsed
        else:
            raise ValueError(f"Invalid type: {record_type}")

        json_str = self.format_log(json_dict)
        self._logger.info(json_str)

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
                # record the previous span before recording the unrelated stop event
                self._record_span(self._last_start_span, RecordType.START)
                self._last_start_span = None

        # record the stop event
        self._record_span(span, RecordType.STOP)

    def record_event(self, event: Event, span: Span) -> None:
        if self._last_start_span:
            self._record_span(self._last_start_span, RecordType.START)
            self._last_start_span = None
        event_json = {
            "type": RecordType.EVENT.value,
            "name": span.name.value,
            "event": event.to_json(),
        }
        json_str = self.format_log(event_json)
        self._logger.info(json_str)

    def record_error(self, event: ExceptionEvent, span: Span) -> None:
        if self._last_start_span:
            self._record_span(self._last_start_span, RecordType.START)
            self._last_start_span = None
        event_json = {
            "type": RecordType.ERROR.value,
            "name": span.name.value,
            "event": event.to_json(),
        }
        json_str = self.format_log(event_json)
        self._logger.error(json_str)

    def close(self) -> None:
        if self._last_start_span:
            _logger.warning(f"Span {self._last_start_span.id} was not closed")
