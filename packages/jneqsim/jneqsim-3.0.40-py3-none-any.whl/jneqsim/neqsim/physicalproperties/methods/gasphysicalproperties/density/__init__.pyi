
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import jneqsim.neqsim.physicalproperties.methods.gasphysicalproperties
import jneqsim.neqsim.physicalproperties.methods.methodinterface
import jneqsim.neqsim.physicalproperties.system
import typing



class Density(jneqsim.neqsim.physicalproperties.methods.gasphysicalproperties.GasPhysicalPropertyMethod, jneqsim.neqsim.physicalproperties.methods.methodinterface.DensityInterface):
    def __init__(self, physicalProperties: jneqsim.neqsim.physicalproperties.system.PhysicalProperties): ...
    def calcDensity(self) -> float: ...
    def clone(self) -> 'Density': ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("jneqsim.neqsim.physicalproperties.methods.gasphysicalproperties.density")``.

    Density: typing.Type[Density]
