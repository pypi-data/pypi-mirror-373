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
import logging
import sys
import time
from datetime import datetime
from typing import Optional


def get_logger(
    name: str, level: int = logging.INFO, propagate: bool = False, format: Optional[str] = None
) -> logging.Logger:
    """Initialize a Python logger configured with timestamp and INFO level.

    Args:
        name: Name of the logger
        level: Logging level

    Returns:
        logging.Logger: Configured Python logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # this prevents the logger from propagating to the root logger
    logger.propagate = propagate

    # Check if this logger already has handlers configured
    if len(logger.handlers) > 0:
        return logger

    # Create file handler with timestamp in filename if the log_file is provided, otherwise create a stream handler for stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    if format is None:
        format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(format)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def get_current_time() -> float:
    """
    Get the start time in seconds since epoch.
    """
    return time.perf_counter()


def get_elapsed_time(start_time: float) -> float:
    """
    Get the elapsed time in seconds since the start time.
    """
    return time.perf_counter() - start_time


def get_timestamp_in_local_timezone() -> datetime:
    """
    Get the current time in the local timezone.
    """
    return datetime.now().astimezone()
