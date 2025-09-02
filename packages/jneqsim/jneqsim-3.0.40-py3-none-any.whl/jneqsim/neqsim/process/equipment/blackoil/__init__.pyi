
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import java.lang
import jneqsim.neqsim.blackoil
import typing



class BlackOilSeparator:
    def __init__(self, string: typing.Union[java.lang.String, str], systemBlackOil: jneqsim.neqsim.blackoil.SystemBlackOil, double: float, double2: float): ...
    def getGasOut(self) -> jneqsim.neqsim.blackoil.SystemBlackOil: ...
    def getInlet(self) -> jneqsim.neqsim.blackoil.SystemBlackOil: ...
    def getName(self) -> java.lang.String: ...
    def getOilOut(self) -> jneqsim.neqsim.blackoil.SystemBlackOil: ...
    def getWaterOut(self) -> jneqsim.neqsim.blackoil.SystemBlackOil: ...
    def run(self) -> None: ...
    def setInlet(self, systemBlackOil: jneqsim.neqsim.blackoil.SystemBlackOil) -> None: ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("jneqsim.neqsim.process.equipment.blackoil")``.

    BlackOilSeparator: typing.Type[BlackOilSeparator]
