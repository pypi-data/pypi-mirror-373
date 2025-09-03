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
import traceback
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from training_telemetry.metrics import EventMetric, EventMetrics
from training_telemetry.utils import get_timestamp_in_local_timezone


class EventName(str, Enum):
    """
    Enum class representing different names of predefined training events.
    """

    # An event representing the start of a span.
    SPAN_START = "span_start"
    # An event representing the stop of a span.
    SPAN_STOP = "span_stop"
    # An event representing an error.
    ERROR = "error"
    # An event representing span attributes, normally containing attributes (metrics) for the span. These attributes
    # can normally be sent with the SPAN_START event, but in some cases, the application config to generate the attributes
    # may not be not available early enough to be sent with the SPAN_START event, for example in the case of ApplicationMetrics.
    SPAN_ATTRIBUTES = "span_attributes"
    # An event representing multiple training iterations reported in aggregated form. This is normally used for logging
    # application progress in a training loop using the iteration metrics, which contain average values for a number of
    # iterations. The event timestamp reflects when the iterations are logged, not when they were executed. The reason we
    # need this event is because the training loop is too long as a single span, and we want to report the progress
    # more frequently. For eval and test loops on the other hand, we can report the metrics at the end of the loop, or span.
    TRAINING_ITERATIONS = "training_iterations"


class Event:
    """
    A class representing a training event. Each event has a name, timestamp,
    and a set of metrics. Timestamps are automatically set to the local timezone.

    Attributes:
        name: The name of the event, either a predefined event name or a custom event name.
        timestamp: indicates when the event occurred.
        metrics: Optional dictionary of event metrics.
    """

    def __init__(
        self,
        name: EventName | str,
        timestamp: datetime,
        metrics: Optional[EventMetrics] = None,
    ):
        self.name = name
        self.timestamp = timestamp
        self.metrics = metrics if metrics is not None else EventMetrics()

        if self.timestamp.tzinfo is None:
            self.timestamp = self.timestamp.astimezone()

    @property
    def name_str(self) -> str:
        return self.name.value if isinstance(self.name, Enum) else self.name

    @classmethod
    def create(cls, name: EventName | str, metrics: Optional[EventMetrics] = None) -> "Event":
        """
        Create a new event with the given name and metrics.
        """
        return cls(name=name, timestamp=get_timestamp_in_local_timezone(), metrics=metrics)

    def with_metrics(self, metrics: EventMetrics) -> "Event":
        """
        Create a new event with the same name and timestamp but with the given metrics added to the existing metrics.
        """
        merged_metrics = EventMetrics.merge(self.metrics, metrics)
        return Event(name=self.name, timestamp=self.timestamp, metrics=merged_metrics)

    def add_metric(self, name: str, value: Any) -> EventMetric:
        """
        Create a metric with the given name and value and add it to the event.

        Args:
            name: The name of the metric.
            value: The value of the metric.

        Returns:
            The metric.
        """
        self.metrics.add_metric(name, value)
        return self.metrics[name]

    def add_metrics(self, metrics: EventMetrics) -> None:
        """
        Add a dictionary of metrics to the event.
        """
        self.metrics.update(metrics)

    def to_json(self) -> dict[str, Any]:
        """Serialize the Event to a JSON-compatible dictionary.

        Returns:
            dict: JSON-serializable representation of the Event
        """
        ret = {
            "name": self.name.value if isinstance(self.name, Enum) else self.name,
            "timestamp": self.timestamp.isoformat(),
        }
        if self.metrics:
            ret["metrics"] = self.metrics.to_json()  # type: ignore
        return ret

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> "Event":
        """Create an Event instance from a JSON-compatible dictionary.

        Args:
            data: Dictionary containing the event data

        Returns:
            Event: New Event instance created from the data
        """
        name = Event._get_event_name(data["name"])
        if name == EventName.ERROR:
            return ExceptionEvent.from_json(data)
        else:
            return cls(
                name=name,
                timestamp=datetime.fromisoformat(data["timestamp"]),
                metrics=EventMetrics.from_json(data["metrics"]) if "metrics" in data else EventMetrics(),
            )

    @classmethod
    def _get_event_name(cls, data: str) -> EventName | str:
        try:
            return EventName(data)
        except ValueError:
            return data


class ExceptionEvent(Event):
    """An event that represents an error and contains an error message and an exception."""

    def __init__(
        self,
        timestamp: datetime,
        error_message: str,
        exception_type: Optional[str] = None,
        exception_message: Optional[str] = None,
        exception_traceback: Optional[str] = None,
        metrics: Optional[EventMetrics] = None,
    ):
        super().__init__(EventName.ERROR, timestamp, metrics)
        self.error_message = error_message
        self.exception_type = exception_type
        self.exception_message = exception_message
        self.exception_traceback = exception_traceback

        if self.timestamp.tzinfo is None:
            self.timestamp = self.timestamp.astimezone()

        if exception_type is not None and self.exception_traceback is None:
            self.exception_traceback = traceback.format_exc()

    @classmethod
    def create(cls, error_message: str, exception: Optional[Exception] = None, exception_traceback: Optional[str] = None) -> "ExceptionEvent":  # type: ignore[override]
        """
        Create a new error event with the given error message, exception and traceback.
        """
        return cls(
            timestamp=get_timestamp_in_local_timezone(),
            error_message=error_message,
            exception_type=exception.__class__.__name__ if exception else None,
            exception_message=str(exception) if exception else None,
            exception_traceback=exception_traceback,
        )

    def to_json(self) -> dict[str, Any]:
        """Serialize the ExceptionEvent to a JSON-compatible dictionary.

        Returns:
            dict: JSON-serializable representation of the ExceptionEvent
        """
        ret = {
            "name": self.name.value if isinstance(self.name, Enum) else self.name,
            "timestamp": self.timestamp.isoformat(),
            "error_message": json.dumps(self.error_message),
        }

        if self.exception_type is not None:
            assert self.exception_traceback is not None
            assert self.exception_message is not None
            ret["exception_type"] = json.dumps(self.exception_type)
            ret["exception_message"] = json.dumps(self.exception_message)
            ret["exception_traceback"] = json.dumps(self.exception_traceback)

        return ret

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> "Event":
        """Create an ExceptionEvent instance from a JSON-compatible dictionary.

        Args:
            data: Dictionary containing the exception event data

        Returns:
            ExceptionEvent: New ExceptionEvent instance created from the data
        """

        def _decode_value(value: Any) -> Any:
            try:
                if isinstance(value, str) and value.startswith('"'):
                    return json.loads(value)
                else:
                    return value
            except (json.JSONDecodeError, TypeError):
                return value

        return cls(
            timestamp=datetime.fromisoformat(data["timestamp"]),
            error_message=_decode_value(data["error_message"]),
            exception_type=_decode_value(data["exception_type"]) if "exception_type" in data else None,
            exception_message=_decode_value(data["exception_message"]) if "exception_message" in data else None,
            exception_traceback=_decode_value(data["exception_traceback"]) if "exception_traceback" in data else None,
            metrics=EventMetrics.from_json(data["metrics"]) if "metrics" in data else EventMetrics(),
        )
