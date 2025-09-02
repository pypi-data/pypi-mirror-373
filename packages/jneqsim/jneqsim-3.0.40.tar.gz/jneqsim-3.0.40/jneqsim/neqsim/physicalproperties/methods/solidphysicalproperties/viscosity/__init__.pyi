
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import jneqsim.neqsim.physicalproperties.methods.methodinterface
import jneqsim.neqsim.physicalproperties.methods.solidphysicalproperties
import jneqsim.neqsim.physicalproperties.system
import typing



class Viscosity(jneqsim.neqsim.physicalproperties.methods.solidphysicalproperties.SolidPhysicalPropertyMethod, jneqsim.neqsim.physicalproperties.methods.methodinterface.ViscosityInterface):
    pureComponentViscosity: typing.MutableSequence[float] = ...
    def __init__(self, physicalProperties: jneqsim.neqsim.physicalproperties.system.PhysicalProperties): ...
    def calcPureComponentViscosity(self) -> None: ...
    def calcViscosity(self) -> float: ...
    def clone(self) -> 'Viscosity': ...
    def getPureComponentViscosity(self, int: int) -> float: ...
    def getViscosityPressureCorrection(self, int: int) -> float: ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("jneqsim.neqsim.physicalproperties.methods.solidphysicalproperties.viscosity")``.

    Viscosity: typing.Type[Viscosity]
