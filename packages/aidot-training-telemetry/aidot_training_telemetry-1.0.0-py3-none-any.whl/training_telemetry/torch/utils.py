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
import os
from typing import Optional

import torch.distributed as dist


def get_rank(group: Optional[dist.ProcessGroup] = None) -> int:
    """Get the rank (GPU device) of the worker.

    Returns:
        rank (int): The rank of the worker.
    """
    rank = int(os.getenv("RANK", "0"))
    if dist.is_available() and dist.is_initialized():
        rank = dist.get_rank(group)
    return rank


def get_world_size(group: Optional[dist.ProcessGroup] = None) -> int:
    """Get world size. How many GPUs are available in this job.

    Returns:
        world_size (int): The total number of GPUs available in this job.
    """
    world_size = int(os.getenv("WORLD_SIZE", "1"))
    if dist.is_available() and dist.is_initialized():
        world_size = dist.get_world_size(group)
    return world_size


def is_rank0() -> bool:
    """Check if current process is the master GPU.

    Returns:
        (bool): True if this function is called from the master GPU, else False.
    """
    return get_rank() == 0


def barrier() -> None:
    """Barrier for all ranks."""
    if dist.is_available() and dist.is_initialized():
        dist.barrier()
