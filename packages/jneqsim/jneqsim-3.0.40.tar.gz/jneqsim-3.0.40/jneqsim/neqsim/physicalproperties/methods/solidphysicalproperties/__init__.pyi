
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import jneqsim.neqsim.physicalproperties.methods
import jneqsim.neqsim.physicalproperties.methods.solidphysicalproperties.conductivity
import jneqsim.neqsim.physicalproperties.methods.solidphysicalproperties.density
import jneqsim.neqsim.physicalproperties.methods.solidphysicalproperties.diffusivity
import jneqsim.neqsim.physicalproperties.methods.solidphysicalproperties.viscosity
import jneqsim.neqsim.physicalproperties.system
import typing



class SolidPhysicalPropertyMethod(jneqsim.neqsim.physicalproperties.methods.PhysicalPropertyMethod):
    def __init__(self, physicalProperties: jneqsim.neqsim.physicalproperties.system.PhysicalProperties): ...
    def setPhase(self, physicalProperties: jneqsim.neqsim.physicalproperties.system.PhysicalProperties) -> None: ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("jneqsim.neqsim.physicalproperties.methods.solidphysicalproperties")``.

    SolidPhysicalPropertyMethod: typing.Type[SolidPhysicalPropertyMethod]
    conductivity: jneqsim.neqsim.physicalproperties.methods.solidphysicalproperties.conductivity.__module_protocol__
    density: jneqsim.neqsim.physicalproperties.methods.solidphysicalproperties.density.__module_protocol__
    diffusivity: jneqsim.neqsim.physicalproperties.methods.solidphysicalproperties.diffusivity.__module_protocol__
    viscosity: jneqsim.neqsim.physicalproperties.methods.solidphysicalproperties.viscosity.__module_protocol__
