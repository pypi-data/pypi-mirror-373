
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import jneqsim.neqsim.process.equipment
import jneqsim.neqsim.process.mechanicaldesign.separator
import typing



class AbsorberMechanicalDesign(jneqsim.neqsim.process.mechanicaldesign.separator.SeparatorMechanicalDesign):
    def __init__(self, processEquipmentInterface: jneqsim.neqsim.process.equipment.ProcessEquipmentInterface): ...
    def calcDesign(self) -> None: ...
    def getOuterDiameter(self) -> float: ...
    def getWallThickness(self) -> float: ...
    def readDesignSpecifications(self) -> None: ...
    def setDesign(self) -> None: ...
    def setOuterDiameter(self, double: float) -> None: ...
    def setWallThickness(self, double: float) -> None: ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("jneqsim.neqsim.process.mechanicaldesign.absorber")``.

    AbsorberMechanicalDesign: typing.Type[AbsorberMechanicalDesign]
