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


class RecordType(Enum):
    """
    The type of record to be used by backends that log to a file, e.g. FileBackend and LoggerBackend.
    """

    # The start of a span.
    START = "start"
    # The end of a span.
    STOP = "stop"
    # A complete span, that is the start and stop of a span are combined into a single record for efficiency.
    COMPLETE = "complete"
    # A single event that can occurr anytime in a span, e.g. a training iteration in a training loop.
    EVENT = "event"
    # An error is a special event that is used to record an exception or another error message.
    ERROR = "error"
