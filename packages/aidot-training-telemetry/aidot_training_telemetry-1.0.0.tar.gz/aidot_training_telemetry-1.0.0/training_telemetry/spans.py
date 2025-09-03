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
from enum import Enum
from typing import Optional

from training_telemetry.duration import Duration
from training_telemetry.events import Event, EventName
from training_telemetry.metrics import EventMetric, EventMetrics
from training_telemetry.verbosity import Verbosity


class SpanName(str, Enum):
    """
    Enum class representing names of predefined spans.
    """

    ##
    ## Long running spans
    ##

    # The entire duration of the main or launcher function of the application.
    MAIN_FUNCTION = "main_function"
    # The entire duration of the training loop.
    TRAINING_LOOP = "training_loop"
    # The entire duration of a validation phase.
    VALIDATION_LOOP = "validation_loop"

    ##
    ## Initialization spans
    ##

    # The initialization of the distributed training code.
    DIST_INIT = "distributed_code_initialization"
    # The initialization of the data loader.
    DATA_LOADER_INIT = "data_loader_initialization"
    # The initialization of the model.
    MODEL_INIT = "model_initialization"
    # The initialization of the optimizer.
    OPTIMIZER_INIT = "optimizer_initialization"

    ##
    ## Checkpoint spans
    ##

    # The loading of a checkpoint.
    CHECKPOINT_LOAD = "checkpoint_load"
    # The saving of a checkpoint synchronously.
    CHECKPOINT_SAVE_SYNC = "checkpoint_save_sync"
    # The saving of a checkpoint asynchronously.
    # Only report exposed checkpoint time, i.e. the time the training loop was blocked for.
    CHECKPOINT_SAVE_ASYNC = "checkpoint_save_async"
    # The finalization of an asynchronous checkpoint save.
    CHECKPOINT_SAVE_FINALIZATION = "checkpoint_save_finalization"

    ##
    ## Very short spans, normally used for profiling backends
    ##

    # A single iteration in either the training or validation loop, also known as a single step.
    ITERATION = "iteration"
    # The loading of data inside a training iteration.
    DATA_LOADING = "data_loading"
    # The forward pass inside a training iteration.
    MODEL_FORWARD = "model_forward"
    # The zeroing of the gradients.
    ZERO_GRAD = "zero_grad"
    # The backward pass inside a training iteration.
    MODEL_BACKWARD = "model_backward"
    # The update of the optimizer.
    OPTIMIZER_UPDATE = "optimizer_update"


class SpanColor(str, Enum):
    """
    The color of the span, this is optional and currently only used for NVTX spans.
    Here we list the colors that are supported by NVTX.
    """

    UNSET = "unset"
    GREEN = "green"
    BLUE = "blue"
    YELLOW = "yellow"
    PURPLE = "purple"
    RAPIDS = "rapids"
    CYAN = "cyan"
    RED = "red"
    WHITE = "white"
    DARK_GREEN = "darkgreen"
    ORANGE = "orange"


class Span:
    """
    A span records an operation that takes some time to complete. It is identified by a name,
    and has a duration and an optional color for backends that support colors such as NVTX.
    A span starts and ends with an event, and can have optional child events.
    """

    def __init__(
        self,
        id: uuid.UUID,
        name: SpanName,
        start_event: Event,
        start_time: Optional[float] = None,
        color: Optional[SpanColor] = None,
        verbosity: Verbosity = Verbosity.INFO,
    ):
        self.id: uuid.UUID = id
        self.name: SpanName = name
        self.duration: Duration = Duration.create(start_time=start_time, start=True)
        self.events: list[Event] = [start_event]
        self.metrics: EventMetrics = EventMetrics()
        self.color: Optional[SpanColor] = color
        self.verbosity: Verbosity = verbosity

    @classmethod
    def create(
        cls,
        name: SpanName,
        color: Optional[SpanColor] = None,
        start_time: Optional[float] = None,
        verbosity: Verbosity = Verbosity.INFO,
        metrics: Optional[EventMetrics] = None,
    ) -> "Span":
        """
        Create a new span with the given parameters.

        Args:
            name: The name of the span.
            start: The start event.
            color: The optional color of the span.
            start_time: The optional start time of the span, the current timestamp will be used if not specified.
            verbosity: The verbosity of the span, INFO by default.
            metrics: The optional metrics of the span, the start event will have these metrics added to it.
        """
        start_event = Event.create(name=EventName.SPAN_START, metrics=metrics)
        return cls(
            id=uuid.uuid4(), name=name, start_event=start_event, start_time=start_time, color=color, verbosity=verbosity
        )

    @property
    def start_event(self) -> Event:
        assert isinstance(self.events[0], Event)
        return self.events[0]

    @property
    def stop_event(self) -> Optional[Event]:
        return self.events[-1] if len(self.events) > 1 and not self.duration.running else None

    def stop(self) -> None:
        if not self.duration.running:
            return  # already stopped
        self.add_event(Event.create(name=EventName.SPAN_STOP, metrics=self.metrics))
        self.duration.stop(reset=False)

    def add_event(self, event: Event) -> None:
        self.events.append(event)

    def add_metric(self, name: str, value: float) -> EventMetric:
        """
        Add a metric to the span. This metric will be recorded with the end event.
        If you need to record a metric before the span ends, use the add_event() method,
        making sure the event has the metric you want to record.

        Args:
            name: The name of the metric.
            value: The value of the metric.

        Returns:
            The metric.
        """
        self.metrics[name] = EventMetric(name=name, value=value)
        return self.metrics[name]

    def add_metrics(self, metrics: EventMetrics) -> None:
        """
        Add a dictionary of metrics to the event.
        """
        self.metrics.update(metrics)
