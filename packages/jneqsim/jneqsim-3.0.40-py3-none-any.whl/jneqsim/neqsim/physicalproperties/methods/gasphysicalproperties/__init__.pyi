
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import jneqsim.neqsim.physicalproperties.methods
import jneqsim.neqsim.physicalproperties.methods.gasphysicalproperties.conductivity
import jneqsim.neqsim.physicalproperties.methods.gasphysicalproperties.density
import jneqsim.neqsim.physicalproperties.methods.gasphysicalproperties.diffusivity
import jneqsim.neqsim.physicalproperties.methods.gasphysicalproperties.viscosity
import jneqsim.neqsim.physicalproperties.system
import typing



class GasPhysicalPropertyMethod(jneqsim.neqsim.physicalproperties.methods.PhysicalPropertyMethod):
    binaryMolecularDiameter: typing.MutableSequence[typing.MutableSequence[float]] = ...
    binaryEnergyParameter: typing.MutableSequence[typing.MutableSequence[float]] = ...
    binaryMolecularMass: typing.MutableSequence[typing.MutableSequence[float]] = ...
    def __init__(self, physicalProperties: jneqsim.neqsim.physicalproperties.system.PhysicalProperties): ...
    def setPhase(self, physicalProperties: jneqsim.neqsim.physicalproperties.system.PhysicalProperties) -> None: ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("jneqsim.neqsim.physicalproperties.methods.gasphysicalproperties")``.

    GasPhysicalPropertyMethod: typing.Type[GasPhysicalPropertyMethod]
    conductivity: jneqsim.neqsim.physicalproperties.methods.gasphysicalproperties.conductivity.__module_protocol__
    density: jneqsim.neqsim.physicalproperties.methods.gasphysicalproperties.density.__module_protocol__
    diffusivity: jneqsim.neqsim.physicalproperties.methods.gasphysicalproperties.diffusivity.__module_protocol__
    viscosity: jneqsim.neqsim.physicalproperties.methods.gasphysicalproperties.viscosity.__module_protocol__
