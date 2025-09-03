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
from contextlib import contextmanager
from typing import Generator, Optional

from training_telemetry.metrics import CheckpointMetrics, EventMetrics
from training_telemetry.provider import Provider
from training_telemetry.recorder import Recorder
from training_telemetry.spans import Span, SpanColor, SpanName
from training_telemetry.verbosity import Verbosity


def get_recorder() -> Recorder:
    """Shortcut for getting the recorder from the provider."""
    return Provider.instance().recorder


@contextmanager
def timed_span(
    name: SpanName,
    color: Optional[SpanColor] = None,
    start_time: Optional[float] = None,
    verbosity: Verbosity = Verbosity.INFO,
    metrics: Optional[EventMetrics] = None,
) -> Generator[Span, None, None]:
    """Context manager for recording a span with timing and metrics.
    The initial set of metrics will be recorded with the start event. If the user adds more metrics to the span,
    they will be recorded with the end event.

    Args:
        name: The name/type of the span to record
        start_time: The start time of the span
        color: The color to use for the span
        verbosity: The verbosity level to use for recording the span
        metrics: Optional dictionary of metrics to record with the start event

    Yields:
        the span
    """
    recorder = get_recorder()
    span = recorder.start(name=name, color=color, start_time=start_time, verbosity=verbosity, metrics=metrics)

    try:
        yield span
    except Exception as e:
        recorder.error(f"Error in {name}:", e, span)
        raise e
    finally:
        recorder.stop(span)


@contextmanager
def running(
    start_time: Optional[float] = None,
    metrics: Optional[EventMetrics] = None,
    verbosity: Verbosity = Verbosity.INFO,
    color: Optional[SpanColor] = None,
) -> Generator[Span, None, None]:
    """
    Context manager for recording events for the entire application duration.
    This context or function annotation can be used for the main function.
    This will result in any exceptions that occur and that are not caught by the application
    to be recorded as an error event.

    Args:
        metrics: Optional dictionary of metrics to record with the start event
        verbosity: The verbosity level to use for recording the span
        color: The color to use for the span

    Yields:
        the span
    """
    with timed_span(
        name=SpanName.MAIN_FUNCTION,
        color=color,
        start_time=start_time,
        verbosity=verbosity,
        metrics=metrics,
    ) as span:
        yield span


@contextmanager
def training(
    start_time: Optional[float] = None,
    metrics: Optional[EventMetrics] = None,
    verbosity: Verbosity = Verbosity.INFO,
    color: Optional[SpanColor] = None,
) -> Generator[Span, None, None]:
    """Context manager for recording the entire training loop.
    This is just a wrapper of timed_span() with the event name set to TRAINING_LOOP.

    Args:
        metrics: Optional dictionary of metrics to record with the start event
        verbosity: The verbosity level to use for recording the span
        color: The color to use for the span

    Yields:
        the span
    """
    with timed_span(
        name=SpanName.TRAINING_LOOP,
        color=color,
        start_time=start_time,
        verbosity=verbosity,
        metrics=metrics,
    ) as span:
        yield span


@contextmanager
def validation(
    start_time: Optional[float] = None,
    metrics: Optional[EventMetrics] = None,
    verbosity: Verbosity = Verbosity.INFO,
    color: Optional[SpanColor] = None,
) -> Generator[Span, None, None]:
    """Context manager for recording the entire validation loop.
    This is just a wrapper of timed_span() with the event name set to VALIDATION_RUNNING.

    Args:
        metrics: Optional dictionary of metrics to record with the start event
        verbosity: The verbosity level to use for recording the span
        color: The color to use for the span

    Yields:
        the span
    """
    with timed_span(
        name=SpanName.VALIDATION_LOOP,
        color=color,
        start_time=start_time,
        verbosity=verbosity,
        metrics=metrics,
    ) as span:
        yield span


@contextmanager
def checkpoint_save(
    start_time: Optional[float] = None,
    metrics: Optional[CheckpointMetrics] = None,
    verbosity: Verbosity = Verbosity.INFO,
    color: Optional[SpanColor] = None,
) -> Generator[Span, None, None]:
    """
    Context manager for recording a checkpoint save with timing and metrics. This is just
    a wrapper of timed_span() with the event name set to CHECKPOINT_SAVE.

    Args:
        metrics: Optional dictionary of metrics to record with the start event
        verbosity: The verbosity level to use for recording the span
        color: The color to use for the span

    Yields:
        the span
    """
    with timed_span(
        name=SpanName.CHECKPOINT_SAVE_SYNC,
        color=color,
        start_time=start_time,
        verbosity=verbosity,
        metrics=metrics,
    ) as span:
        yield span
