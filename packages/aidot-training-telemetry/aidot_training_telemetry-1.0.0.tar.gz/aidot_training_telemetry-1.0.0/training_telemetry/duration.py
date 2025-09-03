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
from dataclasses import dataclass
from typing import Optional

from training_telemetry.utils import get_current_time, get_elapsed_time


@dataclass
class Duration:
    """
    A class representing the duration of a span. It can be used to measure the duration
    of a span, or directly by applications to measure custom durations with high precision
    """

    start_time: float
    elapsed: float
    running: bool

    @classmethod
    def create(cls, start_time: Optional[float] = None, start: bool = True) -> "Duration":
        """
        Create a new Duration instance and optionally start it.

        Args:
            start_time: The time to start the duration measurement, if start is True. If not provided, the current time will be used.
            start: Whether to start the duration measurement immediately.

        Returns:
            A new Duration instance.
        """
        ret = cls(start_time=0, elapsed=0, running=False)
        if start:
            if start_time is None:
                start_time = get_current_time()
            ret.start(start_time)
        return ret

    def start(self, start_time: Optional[float] = None) -> None:
        """
        Start the duration measurement.

        Args:
            start_time: The time to start the duration measurement. If not provided, the current time will be used.
        """
        if self.running:
            raise ValueError("Duration is already running")
        if start_time is None:
            start_time = get_current_time()
        self.start_time = start_time
        self.running = True

    def stop(self, reset: bool = False) -> float:
        """
        Stop the duration measurement.

        Args:
            reset: Whether to reset the duration measurement, otherwise the elapsed time will be accumulated.

        Returns:
            The elapsed time.
        """
        if not self.running:
            raise ValueError("Duration is not running")
        self.elapsed += get_elapsed_time(self.start_time)
        self.running = False
        if reset:
            ret = self.elapsed
            self.reset()
            return ret
        else:
            return self.elapsed

    def reset(self, start_time: Optional[float] = None, start: bool = False) -> None:
        """
        Reset the duration and optionally re-start it.

        Args:
            start_time: The time to start the duration measurement, if start is True. If not provided, the current time will be used.
            start: Whether to start the duration measurement immediately.
        """
        self.start_time = 0
        self.elapsed = 0
        self.running = False
        if start:
            self.start(start_time)
