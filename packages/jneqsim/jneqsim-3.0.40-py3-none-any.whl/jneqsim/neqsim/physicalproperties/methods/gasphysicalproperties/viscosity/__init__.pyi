
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import jneqsim.neqsim.physicalproperties.methods.gasphysicalproperties
import jneqsim.neqsim.physicalproperties.methods.methodinterface
import jneqsim.neqsim.physicalproperties.system
import typing



class Viscosity(jneqsim.neqsim.physicalproperties.methods.gasphysicalproperties.GasPhysicalPropertyMethod, jneqsim.neqsim.physicalproperties.methods.methodinterface.ViscosityInterface):
    def __init__(self, physicalProperties: jneqsim.neqsim.physicalproperties.system.PhysicalProperties): ...
    def clone(self) -> 'Viscosity': ...

class ChungViscosityMethod(Viscosity):
    pureComponentViscosity: typing.MutableSequence[float] = ...
    relativeViscosity: typing.MutableSequence[float] = ...
    Fc: typing.MutableSequence[float] = ...
    omegaVisc: typing.MutableSequence[float] = ...
    def __init__(self, physicalProperties: jneqsim.neqsim.physicalproperties.system.PhysicalProperties): ...
    def calcViscosity(self) -> float: ...
    def getPureComponentViscosity(self, int: int) -> float: ...
    def initChungPureComponentViscosity(self) -> None: ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("jneqsim.neqsim.physicalproperties.methods.gasphysicalproperties.viscosity")``.

    ChungViscosityMethod: typing.Type[ChungViscosityMethod]
    Viscosity: typing.Type[Viscosity]
