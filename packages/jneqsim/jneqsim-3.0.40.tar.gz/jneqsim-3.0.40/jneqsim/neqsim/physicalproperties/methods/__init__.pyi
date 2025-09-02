
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import java.io
import java.lang
import jneqsim.neqsim.physicalproperties.methods.commonphasephysicalproperties
import jneqsim.neqsim.physicalproperties.methods.gasphysicalproperties
import jneqsim.neqsim.physicalproperties.methods.liquidphysicalproperties
import jneqsim.neqsim.physicalproperties.methods.methodinterface
import jneqsim.neqsim.physicalproperties.methods.solidphysicalproperties
import jneqsim.neqsim.physicalproperties.system
import typing



class PhysicalPropertyMethodInterface(java.lang.Cloneable, java.io.Serializable):
    def clone(self) -> 'PhysicalPropertyMethodInterface': ...
    def setPhase(self, physicalProperties: jneqsim.neqsim.physicalproperties.system.PhysicalProperties) -> None: ...
    def tuneModel(self, double: float, double2: float, double3: float) -> None: ...

class PhysicalPropertyMethod(PhysicalPropertyMethodInterface):
    def __init__(self, physicalProperties: jneqsim.neqsim.physicalproperties.system.PhysicalProperties): ...
    def clone(self) -> 'PhysicalPropertyMethod': ...
    def tuneModel(self, double: float, double2: float, double3: float) -> None: ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("jneqsim.neqsim.physicalproperties.methods")``.

    PhysicalPropertyMethod: typing.Type[PhysicalPropertyMethod]
    PhysicalPropertyMethodInterface: typing.Type[PhysicalPropertyMethodInterface]
    commonphasephysicalproperties: jneqsim.neqsim.physicalproperties.methods.commonphasephysicalproperties.__module_protocol__
    gasphysicalproperties: jneqsim.neqsim.physicalproperties.methods.gasphysicalproperties.__module_protocol__
    liquidphysicalproperties: jneqsim.neqsim.physicalproperties.methods.liquidphysicalproperties.__module_protocol__
    methodinterface: jneqsim.neqsim.physicalproperties.methods.methodinterface.__module_protocol__
    solidphysicalproperties: jneqsim.neqsim.physicalproperties.methods.solidphysicalproperties.__module_protocol__
