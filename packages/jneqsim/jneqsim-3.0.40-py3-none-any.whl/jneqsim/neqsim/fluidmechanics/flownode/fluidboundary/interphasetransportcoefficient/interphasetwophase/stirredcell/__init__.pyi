
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import jneqsim.neqsim.fluidmechanics.flownode
import jneqsim.neqsim.fluidmechanics.flownode.fluidboundary.interphasetransportcoefficient.interphasetwophase.interphasepipeflow
import typing



class InterphaseStirredCellFlow(jneqsim.neqsim.fluidmechanics.flownode.fluidboundary.interphasetransportcoefficient.interphasetwophase.interphasepipeflow.InterphaseStratifiedFlow):
    @typing.overload
    def __init__(self): ...
    @typing.overload
    def __init__(self, flowNodeInterface: jneqsim.neqsim.fluidmechanics.flownode.FlowNodeInterface): ...
    def calcInterphaseHeatTransferCoefficient(self, int: int, double: float, flowNodeInterface: jneqsim.neqsim.fluidmechanics.flownode.FlowNodeInterface) -> float: ...
    def calcInterphaseMassTransferCoefficient(self, int: int, double: float, flowNodeInterface: jneqsim.neqsim.fluidmechanics.flownode.FlowNodeInterface) -> float: ...
    @typing.overload
    def calcWallHeatTransferCoefficient(self, int: int, flowNodeInterface: jneqsim.neqsim.fluidmechanics.flownode.FlowNodeInterface) -> float: ...
    @typing.overload
    def calcWallHeatTransferCoefficient(self, int: int, double: float, flowNodeInterface: jneqsim.neqsim.fluidmechanics.flownode.FlowNodeInterface) -> float: ...
    def calcWallMassTransferCoefficient(self, int: int, double: float, flowNodeInterface: jneqsim.neqsim.fluidmechanics.flownode.FlowNodeInterface) -> float: ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("jneqsim.neqsim.fluidmechanics.flownode.fluidboundary.interphasetransportcoefficient.interphasetwophase.stirredcell")``.

    InterphaseStirredCellFlow: typing.Type[InterphaseStirredCellFlow]
