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
from collections import defaultdict

import nvtx

from training_telemetry.config import BackendType
from training_telemetry.events import Event, ExceptionEvent
from training_telemetry.internal.backend import Backend
from training_telemetry.spans import Span, SpanName
from training_telemetry.utils import get_logger
from training_telemetry.verbosity import Verbosity

_logger = get_logger(__name__)


class NVTXBackend(Backend):
    """Backend implementation that sends telemetry data to NVIDIA Tools Extension (NVTX)."""

    def __init__(self) -> None:
        """Initialize the NVTX backend."""
        self.ranges_by_span_id: dict[uuid.UUID, nvtx.Range] = {}
        self.counts_by_span_name: defaultdict[SpanName, int] = defaultdict(int)

    def type(self) -> BackendType:
        return BackendType.NVTX

    def verbosity(self) -> Verbosity:
        return Verbosity.PROFILING

    def record_start(self, span: Span) -> None:
        """Record the start of a time span."""
        self.counts_by_span_name[span.name] += 1
        name = f"{span.name.value}_{self.counts_by_span_name[span.name]}"
        self.ranges_by_span_id[span.id] = nvtx.start_range(message=name, color=span.color.value if span.color else None)

    def record_stop(self, span: Span) -> None:
        """Record the end of a time span."""
        try:
            range = self.ranges_by_span_id.pop(span.id)
            if range:
                nvtx.end_range(range)
        except KeyError:
            _logger.warning(f"Span {span.id} not found in NVTX ranges")

    def record_event(self, event: Event, span: Span) -> None:
        """Record an event."""
        nvtx.mark(message=event.name_str, color=span.color.value if span.color else None)

    def record_error(self, event: ExceptionEvent, span: Span) -> None:
        """Record an error event."""
        nvtx.mark(message=event.error_message, color=span.color.value if span.color else None)

    def close(self) -> None:
        """Close the NVTX backend."""
        try:
            for range in self.ranges_by_span_id.values():
                nvtx.end_range(range)
        finally:
            self.ranges_by_span_id.clear()
