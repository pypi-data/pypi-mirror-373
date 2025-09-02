
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import java.lang
import java.util
import jneqsim.neqsim.process.equipment
import jneqsim.neqsim.process.equipment.stream
import typing



class Ejector(jneqsim.neqsim.process.equipment.ProcessEquipmentBaseClass):
    def __init__(self, string: typing.Union[java.lang.String, str], streamInterface: jneqsim.neqsim.process.equipment.stream.StreamInterface, streamInterface2: jneqsim.neqsim.process.equipment.stream.StreamInterface): ...
    def getEntrainmentRatio(self) -> float: ...
    def getOutStream(self) -> jneqsim.neqsim.process.equipment.stream.StreamInterface: ...
    @typing.overload
    def run(self) -> None: ...
    @typing.overload
    def run(self, uUID: java.util.UUID) -> None: ...
    def setDiffuserEfficiency(self, double: float) -> None: ...
    def setDischargePressure(self, double: float) -> None: ...
    def setEfficiencyIsentropic(self, double: float) -> None: ...
    def setThroatArea(self, double: float) -> None: ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("jneqsim.neqsim.process.equipment.ejector")``.

    Ejector: typing.Type[Ejector]
