# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT license. See LICENSE for more info.

"""Failing pipeline subclass."""

import logging
from uuid import UUID

import tango
from beartype import beartype

from lima2.client.convert import frame_info_to_shape_dtype
from lima2.client.pipeline import Pipeline
from lima2.client.topology import TopologyKind

# Create a logger
_logger = logging.getLogger(__name__)


@beartype
class Failing(Pipeline):
    tango_class = "LimaProcessingFailing"

    FRAME_SOURCES = {}
    """Available frame sources."""

    def __init__(
        self,
        uuid: UUID,
        proc_devs: list[tango.DeviceProxy],
        topology_kind: TopologyKind,
        timeout: int,
    ):
        super().__init__(
            uuid=uuid, proc_devs=proc_devs, topology_kind=topology_kind, timeout=timeout
        )

    @property
    def channels(self):
        """Return the channel descriptions"""
        return {
            "frame": frame_info_to_shape_dtype(
                {
                    "nb_channels": 1,
                    "dimensions": {"x": 0, "y": 0},
                    "pixel_type": "gray8",
                }
            ),
        }
