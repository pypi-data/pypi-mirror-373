
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import java.lang
import java.util
import jneqsim.neqsim.process.equipment
import typing



class Orifice(jneqsim.neqsim.process.equipment.TwoPortEquipment):
    @typing.overload
    def __init__(self, string: typing.Union[java.lang.String, str]): ...
    @typing.overload
    def __init__(self, string: typing.Union[java.lang.String, str], double: float, double2: float, double3: float, double4: float, double5: float): ...
    def calc_dp(self) -> float: ...
    @staticmethod
    def calculateBetaRatio(double: float, double2: float) -> float: ...
    @staticmethod
    def calculateDischargeCoefficient(double: float, double2: float, double3: float, double4: float, double5: float, string: typing.Union[java.lang.String, str]) -> float: ...
    @staticmethod
    def calculateExpansibility(double: float, double2: float, double3: float, double4: float, double5: float) -> float: ...
    @staticmethod
    def calculateMassFlowRate(double: float, double2: float, double3: float, double4: float, double5: float, double6: float, double7: float, string: typing.Union[java.lang.String, str]) -> float: ...
    @staticmethod
    def calculatePressureDrop(double: float, double2: float, double3: float, double4: float, double5: float) -> float: ...
    @typing.overload
    def run(self) -> None: ...
    @typing.overload
    def run(self, uUID: java.util.UUID) -> None: ...
    def setOrificeParameters(self, double: float, double2: float, double3: float) -> None: ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("jneqsim.neqsim.process.equipment.diffpressure")``.

    Orifice: typing.Type[Orifice]
