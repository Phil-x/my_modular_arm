import asyncio
import random
import struct
import sys


from typing import Any, Dict, List, Mapping, Optional, Tuple

from viam.components.gripper import Gripper



GEOMETRIES = [
    Geometry(center=Pose(x=1, y=2, z=3, o_x=2, o_y=3, o_z=4, theta=20), sphere=Sphere(radius_mm=2)),
    Geometry(center=Pose(x=1, y=2, z=3, o_x=2, o_y=3, o_z=4, theta=20), capsule=Capsule(radius_mm=3, length_mm=8)),
]


class ExampleGripper(Gripper):
    def __init__(self, name: str):
        self.opened = False
        self.is_stopped = True
        super().__init__(name)

    async def open(self, extra: Optional[Dict[str, Any]] = None, **kwargs):
        self.opened = True
        self.is_stopped = False

    async def grab(self, extra: Optional[Dict[str, Any]] = None, **kwargs) -> bool:
        self.opened = False
        self.is_stopped = False
        return random.choice([True, False])

    async def stop(self, extra: Optional[Dict[str, Any]] = None, **kwargs):
        self.is_stopped = True

    async def is_moving(self):
        return not self.is_stopped

    async def get_geometries(self, extra: Optional[Dict[str, Any]] = None, **kwargs) -> List[Geometry]:
        return GEOMETRIES