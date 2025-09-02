
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import jneqsim.neqsim.physicalproperties.methods.commonphasephysicalproperties
import jneqsim.neqsim.physicalproperties.methods.methodinterface
import jneqsim.neqsim.physicalproperties.system
import typing



class Diffusivity(jneqsim.neqsim.physicalproperties.methods.commonphasephysicalproperties.CommonPhysicalPropertyMethod, jneqsim.neqsim.physicalproperties.methods.methodinterface.DiffusivityInterface):
    def __init__(self, physicalProperties: jneqsim.neqsim.physicalproperties.system.PhysicalProperties): ...
    def calcBinaryDiffusionCoefficient(self, int: int, int2: int, int3: int) -> float: ...
    def calcDiffusionCoefficients(self, int: int, int2: int) -> typing.MutableSequence[typing.MutableSequence[float]]: ...
    def calcEffectiveDiffusionCoefficients(self) -> None: ...
    def clone(self) -> 'Diffusivity': ...
    def getEffectiveDiffusionCoefficient(self, int: int) -> float: ...
    def getFickBinaryDiffusionCoefficient(self, int: int, int2: int) -> float: ...
    def getMaxwellStefanBinaryDiffusionCoefficient(self, int: int, int2: int) -> float: ...

class CorrespondingStatesDiffusivity(Diffusivity):
    def __init__(self, physicalProperties: jneqsim.neqsim.physicalproperties.system.PhysicalProperties): ...
    def calcBinaryDiffusionCoefficient(self, int: int, int2: int, int3: int) -> float: ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("jneqsim.neqsim.physicalproperties.methods.commonphasephysicalproperties.diffusivity")``.

    CorrespondingStatesDiffusivity: typing.Type[CorrespondingStatesDiffusivity]
    Diffusivity: typing.Type[Diffusivity]
