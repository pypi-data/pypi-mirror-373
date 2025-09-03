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
import uuid
from typing import Any, Dict

from opentelemetry import context as context_api
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    SpanExporter,
)
from opentelemetry.trace.propagation import _SPAN_KEY
from opentelemetry.trace.status import Status, StatusCode

from training_telemetry.config import BackendType
from training_telemetry.events import Event, ExceptionEvent
from training_telemetry.internal.backend import Backend
from training_telemetry.spans import Span
from training_telemetry.verbosity import Verbosity


class OTLPTracesBackend(Backend):
    """Backend implementation that sends OpenTelemetry traces over OTLP."""

    def __init__(self, exporter: SpanExporter) -> None:
        """Initialize the OpenTelemetry traces backend."""
        self._provider = TracerProvider()
        self._processor = BatchSpanProcessor(exporter)
        self._provider.add_span_processor(self._processor)
        self._tracer = self._provider.get_tracer("training-telemetry")
        self._trace_spans_with_contexts: dict[uuid.UUID, tuple[trace.Span, context_api.Context]] = {}

    def type(self) -> BackendType:
        return BackendType.OTLP_TRACES

    def verbosity(self) -> Verbosity:
        return Verbosity.TRACING

    def record_start(self, span: Span) -> None:
        """Record the start of a time span."""
        attributes = self._get_span_attributes(span)
        trace_span = self._tracer.start_span(
            name=span.name.value,
            start_time=int(span.start_event.timestamp.timestamp() * 1_000_000),
            attributes=attributes,
        )
        context = context_api.set_value(_SPAN_KEY, trace_span)
        self._trace_spans_with_contexts[span.id] = (trace_span, context)
        self.record_event(span.start_event, span)

    def record_stop(self, span: Span) -> None:
        """Record the end of a time span."""
        if span.id not in self._trace_spans_with_contexts:
            raise ValueError(f"Span {span.id} not found")
        if span.stop_event is None:
            raise ValueError(f"Span {span.id} has no stop event")

        self.record_event(span.stop_event, span)
        trace_span, _context = self._trace_spans_with_contexts.pop(span.id)
        attributes = self._get_span_attributes(span)
        trace_span.set_attributes(attributes)
        trace_span.end(int(span.stop_event.timestamp.timestamp() * 1_000_000))

    def record_event(self, event: Event, span: Span, postfix: str = "") -> None:
        """Record an event."""
        if span.id not in self._trace_spans_with_contexts:
            raise ValueError(f"Span {span.id} not found")

        _parent_span, parent_context = self._trace_spans_with_contexts.get(span.id)  # type: ignore
        attributes = self._get_event_attributes(event)

        # There is an API to add an event directly to the parent span, but for long-lived spans,
        # events do not get reported until the span ends, which could be the entire application
        # runtime or training loop time. FIXME: add a property to the span to control this behavior?
        # parent_span.add_event(event.name.value, attributes, event.timestamp.timestamp())

        event_span = self._tracer.start_span(
            name=event.name_str + postfix,
            context=parent_context,
            start_time=int(event.timestamp.timestamp() * 1_000_000),
            attributes=attributes,
        )
        event_span.end(int(event.timestamp.timestamp() * 1_000_000))

    def record_error(self, event: ExceptionEvent, span: Span) -> None:
        if span.id not in self._trace_spans_with_contexts:
            raise ValueError(f"Span {span.id} not found")

        parent_span, parent_context = self._trace_spans_with_contexts.get(span.id)  # type: ignore

        # we could also attache the error directly to the parent span, but this
        # would mean that the error would not be reported until the span ends, which
        # could be the entire application runtime or training loop time. FIXME: add
        # a property to the span to control this behavior?
        event_span = self._tracer.start_span(
            name=event.name_str,
            context=parent_context,
            start_time=int(event.timestamp.timestamp() * 1_000_000),
            attributes=self._get_exception_attributes(event),
        )
        event_span.set_status(Status(status_code=StatusCode.ERROR, description=event.error_message))
        event_span.end(int(event.timestamp.timestamp() * 1_000_000))

    def close(self) -> None:
        """Close the OpenTelemetry backend."""
        self._provider.shutdown()

    def _get_span_attributes(self, span: Span) -> Dict[str, Any]:
        """Get the attributes for a span."""
        attributes = {}
        if span.duration:
            attributes.update({"duration.elapsed": span.duration.elapsed})
        return attributes

    def _get_event_attributes(self, event: Event) -> Dict[str, Any]:
        """Get the attributes for an event, currently only metrics are supported."""
        attributes: Dict[str, Any] = {}

        if event.metrics:
            for name, metric in event.metrics.items():
                attributes[f"metrics.{name}.value"] = metric.value

        return attributes

    def _get_exception_attributes(self, event: ExceptionEvent) -> Dict[str, Any]:
        """Get the attributes for an exception event, if present."""
        attributes: Dict[str, Any] = {}

        if event.exception_type:
            attributes[f"error.exception_type"] = event.exception_type

        if event.exception_message:
            attributes[f"error.exception_message"] = event.exception_message

        if event.exception_traceback:
            attributes[f"error.exception_traceback"] = event.exception_traceback

        return attributes
