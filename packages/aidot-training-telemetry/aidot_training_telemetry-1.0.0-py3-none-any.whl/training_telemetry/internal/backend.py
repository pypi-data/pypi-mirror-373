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

from training_telemetry.config import BackendType
from training_telemetry.events import Event, ExceptionEvent
from training_telemetry.spans import Span
from training_telemetry.verbosity import Verbosity


class Backend(ABC):
    """Abstract base class for all backends."""

    @abstractmethod
    def type(self) -> BackendType:
        """The type of backend."""

    @abstractmethod
    def verbosity(self) -> Verbosity:
        """
        The maximum verbosity level supported by the backend.
        The backend will record only events and spans with a verbosity level smaller or equal than this one
        """

    @abstractmethod
    def record_start(self, span: Span) -> None:
        """Record an event that indicates the start of a time span."""

    @abstractmethod
    def record_stop(self, span: Span) -> None:
        """Record an event that indicates the end of a time span."""

    @abstractmethod
    def record_event(self, event: Event, span: Span) -> None:
        """Record an event that is instantaneous, and belongs to the last span that was started."""

    @abstractmethod
    def record_error(self, event: ExceptionEvent, span: Span) -> None:
        """Record an error event."""

    @abstractmethod
    def close(self) -> None:
        """Close the backend."""
        pass
