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
import traceback
import uuid
from collections import OrderedDict
from typing import Optional

from training_telemetry.events import Event, ExceptionEvent
from training_telemetry.internal.backend import Backend
from training_telemetry.metrics import EventMetrics
from training_telemetry.recorder import Recorder
from training_telemetry.spans import Span, SpanColor, SpanName
from training_telemetry.utils import get_logger
from training_telemetry.verbosity import Verbosity

_logger = get_logger(__name__)


class StandardRecorder(Recorder):
    """
    Standard implementation of the Recorder interface supporting multiple backends and tracking of spans.
    It is possible to create a StandardRecorder with no backends, in which case it will not record anything,
    this is useful if the application is running on thousands of GPUs, in which case the overhead of recording
    from each GPU is too high, and we only want to record from rank zero or a subset of ranks.
    """

    def __init__(self, backends: list[Backend]):
        self._backends = backends.copy()
        self._spans: OrderedDict[uuid.UUID, Span] = OrderedDict()
        if len(self._backends) > 0:
            _logger.debug(f"Initializing StandardRecorder with {len(self._backends)} backends")
        else:
            _logger.debug("Initializing StandardRecorder with no backends, recording is disabled")

    @property
    def backends(self) -> list[Backend]:
        return self._backends

    def start(
        self,
        name: SpanName,
        color: Optional[SpanColor] = None,
        start_time: Optional[float] = None,
        verbosity: Verbosity = Verbosity.INFO,
        metrics: Optional[EventMetrics] = None,
    ) -> Span:
        span = Span.create(name=name, color=color, start_time=start_time, verbosity=verbosity, metrics=metrics)
        self._spans[span.id] = span
        for backend in self._backends:
            try:
                if verbosity <= backend.verbosity():
                    backend.record_start(span)
            except Exception as e:
                _logger.error(f"Error recording start for span {span.id}: {e}")
        return span

    def stop(self, span: Span) -> None:
        if span.id not in self._spans:
            raise ValueError(f"Span {span.id} not found")

        del self._spans[span.id]
        span.stop()
        for backend in self._backends:
            try:
                if span.verbosity <= backend.verbosity():
                    backend.record_stop(span)
            except Exception as e:
                _logger.error(f"Error recording stop for span {span.id}: {e}")

    def event(self, event: Event, span: Optional[Span] = None, verbosity: Verbosity = Verbosity.INFO) -> Event:
        if span is None:
            if self._spans:
                span = next(reversed(self._spans.values()))
            else:
                raise ValueError("No span to add event to")
        else:
            if span.id not in self._spans:
                raise ValueError(f"Span {span.id} not found")

        span.add_event(event)
        for backend in self._backends:
            try:
                if verbosity <= backend.verbosity():
                    backend.record_event(event, span)
            except Exception as e:
                _logger.error(f"Error recording event {event.name} for span {span.id}: {e}")
        return event

    def error(
        self,
        error_message: str,
        exception: Optional[Exception] = None,
        span: Optional[Span] = None,
        verbosity: Verbosity = Verbosity.ERROR,
    ) -> ExceptionEvent:
        if span is None:
            if self._spans:
                span = next(reversed(self._spans.values()))
            else:
                raise ValueError("No span to add event to")
        else:
            if span.id not in self._spans:
                raise ValueError(f"Span {span.id} not found")

        event = ExceptionEvent.create(
            error_message=error_message, exception=exception, exception_traceback=traceback.format_exc()
        )
        span.add_event(event)
        for backend in self._backends:
            try:
                if verbosity <= backend.verbosity():
                    backend.record_error(event, span)
            except Exception as e:
                _logger.error(f"Error recording error {error_message} for span {span.id}: {e}")
        return event

    def close(self) -> None:
        try:
            for span in reversed(self._spans.values()):
                for backend in self._backends:
                    try:
                        if span.verbosity <= backend.verbosity():
                            backend.record_stop(span)
                    except Exception as e:
                        _logger.error(f"Error recording stop for span {span.id}: {e}")
        finally:
            self._spans.clear()
