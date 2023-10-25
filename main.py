import asyncio

from viam.module.module import Module
from viam.components.arm import Arm
from my_modular_arm import MyModularArm
from viam.resource.registry import Registry, ResourceCreatorRegistration

Registry.register_resource_creator(Arm.SUBTYPE, MyModularArm.MODEL, ResourceCreatorRegistration(MyModularArm.new))

async def main():
    """This function creates and starts a new module, after adding all desired
    resources. Resources must be pre-registered. For an example, see the
    `__init__.py` file.
    """
    module = Module.from_args()
    module.add_model_from_registry(Arm.SUBTYPE, MyModularArm.MODEL)
    await module.start()

if __name__ == "__main__":
        asyncio.run(main())