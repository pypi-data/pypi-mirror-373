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
from enum import Enum


class Verbosity(int, Enum):
    """
    The verbosity level associated with a backend. They go from from smallest to highest verbosity.
    A backend will record all events and spans up to a certain verbosity level.
    """

    # A verbosity intended for non rank-0 logging backends, where we only want to log errors.
    ERROR = 0
    # The default verbosity for logging and file backends, normally on rank 0 for logging.
    INFO = 1
    # A backend that supports optimized tracing, such as the OTEL protocol or compressed files, e.g. protobufs.
    TRACING = 3
    # A backend that supports profiling, such as the NVTX backend for the Nsight Systems profiler.
    PROFILING = 4
