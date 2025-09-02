
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import java.lang
import jpype
import jneqsim.neqsim.fluidmechanics.flownode
import jneqsim.neqsim.fluidmechanics.flownode.fluidboundary.heatmasstransfercalc
import jneqsim.neqsim.thermo.system
import typing



class EquilibriumFluidBoundary(jneqsim.neqsim.fluidmechanics.flownode.fluidboundary.heatmasstransfercalc.FluidBoundary):
    @typing.overload
    def __init__(self, flowNodeInterface: jneqsim.neqsim.fluidmechanics.flownode.FlowNodeInterface): ...
    @typing.overload
    def __init__(self, systemInterface: jneqsim.neqsim.thermo.system.SystemInterface): ...
    def calcFluxes(self) -> typing.MutableSequence[float]: ...
    @staticmethod
    def main(stringArray: typing.Union[typing.List[java.lang.String], jpype.JArray]) -> None: ...
    def solve(self) -> None: ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("jneqsim.neqsim.fluidmechanics.flownode.fluidboundary.heatmasstransfercalc.equilibriumfluidboundary")``.

    EquilibriumFluidBoundary: typing.Type[EquilibriumFluidBoundary]
