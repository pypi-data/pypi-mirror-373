
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import jneqsim.neqsim.physicalproperties.methods.methodinterface
import jneqsim.neqsim.physicalproperties.methods.solidphysicalproperties
import jneqsim.neqsim.physicalproperties.system
import typing



class Conductivity(jneqsim.neqsim.physicalproperties.methods.solidphysicalproperties.SolidPhysicalPropertyMethod, jneqsim.neqsim.physicalproperties.methods.methodinterface.ConductivityInterface):
    def __init__(self, physicalProperties: jneqsim.neqsim.physicalproperties.system.PhysicalProperties): ...
    def calcConductivity(self) -> float: ...
    def clone(self) -> 'Conductivity': ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("jneqsim.neqsim.physicalproperties.methods.solidphysicalproperties.conductivity")``.

    Conductivity: typing.Type[Conductivity]
