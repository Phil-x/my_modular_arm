import asyncio
import os
from typing import Any, ClassVar, Dict, Mapping, Optional, Tuple
from typing_extensions import Self

from viam.components.arm import Arm, JointPositions, KinematicsFileFormat, Pose
from viam.operations import run_with_operation
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import ResourceName
from viam.resource.base import ResourceBase
from viam.resource.types import Model, ModelFamily
from viam.logging import getLogger

from viam.utils import ValueTypes
from viam.module.module import Module
#from viam.resource.registry import Registry, ResourceCreatorRegistration

import serial

LOGGER = getLogger(__name__)
ser = serial.Serial()

class MyModularArm(Arm):
    # Subclass the Viam Arm component and implement the required functions
    MODEL: ClassVar[Model] = Model(ModelFamily("acme", "demo"), "myarm")  # refer to Config tab in VIAM 
    armconfig : ComponentConfig = None

    # Starting joint positions / Axis names
    joint_positions = JointPositions(values=[0, 0, 0, 0, 0, 0])
    axis_list = ['X', 'Y', 'Z', 'A', 'B', 'C'] 

    def __init__(self, name: str):
        LOGGER.info(f'Calling __init__')
        super().__init__(name)

    @classmethod
    def new(cls, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]) -> Self:
        arm = cls(config.name)
        LOGGER.info(f'Calling new()')
        #get the Attributes
        arm.usb_port = config.attributes.fields["port"].string_value
        LOGGER.info(f'usb port:{arm.usb_port}')
        arm.usb_baud = config.attributes.fields["baud"].number_value
        LOGGER.info(f'usb baud:{arm.usb_baud}')
        
        ser.baudrate = arm.usb_baud
        ser.port = arm.usb_port
        ser.timeout = 0 #return immediatly if nb char are read - non blocking
        ser.write_timeout = 1  #make write call non blocking.
        ser.open()
        if ser.is_open:
            LOGGER.info('-------- Serial Connection opened -----------')
            LOGGER.info( ser.read(size=1200))
        return arm

    async def get_end_position(self, extra: Optional[Dict[str, Any]] = None, **kwargs) -> Pose:
        raise NotImplementedError()

    async def move_to_position(self, pose: Pose, extra: Optional[Dict[str, Any]] = None, **kwargs):
        raise NotImplementedError()

    async def get_joint_positions(self, extra: Optional[Dict[str, Any]] = None, **kwargs) -> JointPositions:
        return self.joint_positions

    @run_with_operation
    async def move_to_joint_positions(self, positions: JointPositions, extra: Optional[Dict[str, Any]] = None, **kwargs):
        operation = self.get_operation(kwargs)

        self.is_stopped = False

        # positons are ordered from bottom to top of the arm : X,Y,Z,A,B,C -- Assuming positions are in degres
        grbl = "G0"
        if len(positions.values) == len(self.axis_list): 
            for axis, position in  zip(self.axis_list, list(positions.values)):
                 grbl = grbl+' '+axis+str(position)

            grbl = grbl+'\n'
            grbl_cmd = grbl.encode('ascii')

            LOGGER.info(f'move_to_joint_positions - sending GRBL: {grbl}')
            ser.write(grbl_cmd)
            #self.ser.flush()

            grbl_status = ser.read(size=1200)
            if grbl_status == b'ok\n':
                LOGGER.warning('ok')
            else:
                LOGGER.warning(f'grbl message: {grbl_status}')
        else:
            LOGGER.error(f'positions count ({len(positions.values)}) must match axis count ( {len(self.axis_list)})')
        # Check if the operation is cancelled and, if it is, stop the arm's motion
        #if await operation.is_cancelled():
            await self.stop()


        self.joint_positions = positions
        self.is_stopped = True

    async def stop(self, extra: Optional[Dict[str, Any]] = None, **kwargs):
        self.is_stopped = True

    async def is_moving(self) -> bool:
        return not self.is_stopped

    async def get_kinematics(self, **kwargs) -> Tuple[KinematicsFileFormat.ValueType, bytes]:
        dirname = os.path.dirname(__file__)
        filepath = os.path.join(dirname, "./arctos_arm_sva.json")
        with open(filepath, mode="rb") as f:
            file_data = f.read()
        return (KinematicsFileFormat.KINEMATICS_FILE_FORMAT_SVA, file_data)
    
    async def do_command(self, command: Mapping[str, ValueTypes], *, timeout: Optional[float] = None, **kwargs) -> Mapping[str, ValueTypes]:

        result = {key: False for key in command.keys()}
        #Can process several command in on call to this func.
        for (name, args) in command.items():
            if name == 'is_connected':
                if ser.is_open:
                    LOGGER.info('-------- Connectiom is OK -----------')
                else:
                    LOGGER.info('-------- Connection is closed -----------')
                result[name] = True
            elif name == 'GRBL_cmd':
                grbl = ' '.join(args)
                LOGGER.info(f'GRBL_cmd - sending GRBL: {grbl}')
                grbl = grbl +'\n'
                grbl_cmd = grbl.encode('ascii')
                ser.write(grbl_cmd)
                grbl_status = ser.read(size=1200)
                LOGGER.info(grbl_status)
                result[name] = str(grbl_status)
            else:
                raise NotImplementedError()
        
        return result


async def main():
    arm=MyModularArm.new
    print(arm.__name__)

if __name__ == '__main__':
    asyncio.run(main())