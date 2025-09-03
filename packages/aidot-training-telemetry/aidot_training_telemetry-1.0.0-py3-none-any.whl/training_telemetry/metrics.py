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
from dataclasses import dataclass
from enum import Enum
from typing import Any


@dataclass
class EventMetric:
    """
    A metric attached to an event. It can have a single value.
    It is understood that the timestamp of the event is the timestamp of the metric. In OpenTelemetry,
    these metrics are reported as event attributes. For other backends they are serialized
    as a JSON object in the event. For spans they are normally attached to the span end event.
    """

    name: str
    value: Any


class EventMetrics(dict[str, EventMetric]):
    """A set of metrics for an event."""

    def add_metric(self, name: str, value: Any) -> EventMetric:
        """Add a new metric to the set of metrics."""
        self[name] = EventMetric(name, value)
        return self[name]

    def to_json(self) -> dict[str, Any]:
        """Convert all metrics to a JSON-compatible dictionary.

        Returns:
            dict: JSON-serializable representation of all metrics
        """
        return {
            metric.name: json.dumps(metric.value) if isinstance(metric.value, str) else metric.value
            for metric in self.values()
        }

    @classmethod
    def from_json(cls, data: dict) -> "EventMetrics":
        """Create a EventMetrics instance from a JSON-compatible dictionary.

        Args:
            data: Dictionary containing the metrics data

        Returns:
            EventMetrics: New metrics collection created from the data
        """
        metrics = cls()

        def _decode_value(value: Any) -> Any:
            try:
                if isinstance(value, str) and value.startswith('"'):
                    return json.loads(value)
                else:
                    return value
            except (json.JSONDecodeError, TypeError):
                return value

        for name, value in data.items():
            metrics.add_metric(name, _decode_value(value))

        return metrics

    @classmethod
    def merge(cls, metrics: "EventMetrics", other: "EventMetrics") -> "EventMetrics":
        """Merge two sets of metrics."""
        merged = cls()
        for metric in metrics.values():
            merged.add_metric(metric.name, metric.value)
        for metric in other.values():
            merged.add_metric(metric.name, metric.value)
        return merged


class ApplicationMetrics(EventMetrics):
    """A set of metrics for an application."""

    @classmethod
    def create(
        cls,
        rank: int | None = None,
        world_size: int | None = None,
        node_name: str | None = None,
        timezone: str | None = None,
        total_iterations: int | None = None,
        checkpoint_enabled: bool | None = None,
        checkpoint_strategy: str | None = None,
    ) -> "ApplicationMetrics":
        metrics = cls()
        if rank is not None:
            metrics.add_metric("rank", rank)
        if world_size is not None:
            metrics.add_metric("world_size", world_size)
        if node_name is not None:
            metrics.add_metric("node_name", node_name)
        if timezone is not None:
            metrics.add_metric("timezone", timezone)
        if total_iterations is not None:
            metrics.add_metric("total_iterations", total_iterations)
        if checkpoint_enabled is not None:
            metrics.add_metric("checkpoint_enabled", checkpoint_enabled)
        if checkpoint_strategy is not None:
            metrics.add_metric("checkpoint_strategy", checkpoint_strategy)
        return metrics


class IterationMetrics(EventMetrics):
    """
    A set of metrics for one or more iterations, either for model training, validation, or testing.
    For testing and validation, these are normally used to report the metrics at the end of the loop, or span.
    For training, these are normally used to report the metrics using the TRAINING_ITERATIONS event.
    """

    @classmethod
    def create(
        cls,
        current_iteration: int | None = None,
        num_iterations: int | None = None,
        interval: int | None = None,
        average_iteration_time: float | None = None,
        average_forward_time: float | None = None,
        average_backward_time: float | None = None,
        average_dataloader_time: float | None = None,
        tflops: float | None = None,
        tokens_per_second: float | None = None,
        loss: float | None = None,
        batch_size: int | None = None,
    ) -> "IterationMetrics":
        """
        Create a IterationMetrics instance.

        Args:
            current_iteration: The current iteration number of the loop, the last one if reported at the end of the loop
            num_iterations: The total number of iterations in the loop or since last reporting in the case of TRAINING_ITERATIONS
            interval: The interval between the current and previous iteration, where a similar event or span was reported. Note
            that for TRAINING_ITERATIONS, this is normally the same as num_iterations.
            average_iteration_time: The average time per iteration
            average_forward_time: The average model forward time per iteration
            average_backward_time: The average model backward time per iteration
            average_dataloader_time: The average dataloader time per iteration
            tflops: The number of tera-floating point operations per second for each iteration
            tokens_per_second: The number of tokens processed per second for each iteration, needed if tflops cannot be calculated
            loss: The current loss value
            batch_size: The number of samples or tokens processed per iteration, also known as the batch size
        """
        metrics = cls()
        if current_iteration is not None:
            metrics.add_metric("current_iteration", current_iteration)
        if num_iterations is not None:
            metrics.add_metric("num_iterations", num_iterations)
        if interval is not None:
            metrics.add_metric("interval", interval)
        if average_iteration_time is not None:
            metrics.add_metric("average_iteration_time", average_iteration_time)
        if average_forward_time is not None:
            metrics.add_metric("average_forward_time", average_forward_time)
        if average_backward_time is not None:
            metrics.add_metric("average_backward_time", average_backward_time)
        if average_dataloader_time is not None:
            metrics.add_metric("average_dataloader_time", average_dataloader_time)
        if tflops is not None:
            metrics.add_metric("tflops", tflops)
        if tokens_per_second is not None:
            metrics.add_metric("tokens_per_second", tokens_per_second)
        if loss is not None:
            metrics.add_metric("loss", loss)
        if batch_size is not None:
            metrics.add_metric("batch_size", batch_size)
        return metrics


class CheckPointType(str, Enum):
    """The type of checkpoint, global or local."""

    # Global checkpoint, saved to remote storage, and persistent.
    GLOBAL = "global"
    # Local checkpoint, saved to local storage, and non-persistent.
    LOCAL = "local"


class CheckpointMetrics(EventMetrics):
    """
    A set of metrics for a checkpoint save or load events.

    The checkpoint type is either global or local.
    The current iteration is the iteration number at the checkpoint save or load.
    The number of iterations since the previous checkpoint save, not needed for checkpoint load.
    The interval is the number of iterations between the current and previous checkpoint save,
    normally the same as num_iterations unless some iterations were excluded from checkpointing.
    The checkpoint size is the size of the checkpoint in bytes.
    The checkpoint directory is the directory where the checkpoint is saved or loaded from.
    """

    @classmethod
    def create(
        cls,
        checkpoint_type: CheckPointType | None = None,
        current_iteration: int | None = None,
        num_iterations: int | None = None,
        interval: int | None = None,
        checkpoint_size: int | None = None,
        checkpoint_directory: str | None = None,
    ) -> "CheckpointMetrics":
        metrics = cls()
        if checkpoint_type is not None:
            metrics.add_metric("checkpoint_type", checkpoint_type)
        if current_iteration is not None:
            metrics.add_metric("current_iteration", current_iteration)
        if num_iterations is not None:
            metrics.add_metric("num_iterations", num_iterations)
        if interval is not None:
            metrics.add_metric("interval", interval)
        if checkpoint_size is not None:
            metrics.add_metric("checkpoint_size", checkpoint_size)
        if checkpoint_directory is not None:
            metrics.add_metric("checkpoint_directory", checkpoint_directory)
        return metrics
