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
from abc import ABC, abstractmethod
from typing import Optional

from training_telemetry.events import Event, ExceptionEvent
from training_telemetry.metrics import EventMetrics
from training_telemetry.spans import Span, SpanColor, SpanName
from training_telemetry.verbosity import Verbosity


class Recorder(ABC):
    """An abstract base class for creating and recording spans and events."""

    @abstractmethod
    def start(
        self,
        name: SpanName,
        color: Optional[SpanColor] = None,
        start_time: Optional[float] = None,
        verbosity: Verbosity = Verbosity.INFO,
        metrics: Optional[EventMetrics] = None,
    ) -> Span:
        """
        Create a new span and record its start event.

        Args:
            name: The name of the span.
            color: The optional color of the span.
            start_time: The optional start time of the span, the current timestamp will be used if not specified.
            verbosity: The verbosity of the span, INFO by default.
            metrics: The optional metrics of the span, the start event will have these metrics added to it.
        """
        pass

    @abstractmethod
    def stop(self, span: Span) -> None:
        """
        Stop the span and record its end event. The same verbosity level as the start event is used.
        Args:
            span: The span to stop.
        """
        pass

    @abstractmethod
    def event(self, event: Event, span: Optional[Span] = None, verbosity: Verbosity = Verbosity.INFO) -> Event:
        """
        Create a new event and record it immediately.
        The event is added to the last span that was started, unless a span is provided.

        Args:
            event: The event to record.
            span: Optional span to add the event to, the last started span will be used if not specified.
            verbosity: The verbosity level of the event, INFO by default.
        Returns:
            The event recorded.
        """
        pass

    @abstractmethod
    def error(
        self,
        error_message: str,
        exception: Optional[Exception] = None,
        span: Optional[Span] = None,
        verbosity: Verbosity = Verbosity.ERROR,
    ) -> ExceptionEvent:
        """
        Create a new error event with the given error message and exception and record it immediately.
        The error event is added to the last span that was started, unless a span is provided.

        Args:
            error_message: The message of the error event.
            exception: The exception of the error event.
            span: Optional span to add the error event to, the last started span will be used if not specified.
            verbosity: The verbosity level of the error event, ERROR by default.
        Returns:
            The error event recorded.
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """
        Close the recorder and release any resources.
        All spans that were previously started will be ended and thei end events recorded at the current time.
        Once the recorder is closed, it cannot be used again.
        """
        pass
