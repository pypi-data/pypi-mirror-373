
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import jneqsim.neqsim.fluidmechanics.flownode
import jneqsim.neqsim.fluidmechanics.flownode.onephasenode.onephasepipeflownode
import jneqsim.neqsim.fluidmechanics.geometrydefinitions
import jneqsim.neqsim.thermo.system
import typing



class onePhaseFlowNode(jneqsim.neqsim.fluidmechanics.flownode.FlowNode):
    @typing.overload
    def __init__(self): ...
    @typing.overload
    def __init__(self, systemInterface: jneqsim.neqsim.thermo.system.SystemInterface): ...
    @typing.overload
    def __init__(self, systemInterface: jneqsim.neqsim.thermo.system.SystemInterface, geometryDefinitionInterface: jneqsim.neqsim.fluidmechanics.geometrydefinitions.GeometryDefinitionInterface): ...
    def calcReynoldsNumber(self) -> float: ...
    def clone(self) -> 'onePhaseFlowNode': ...
    def increaseMolarRate(self, double: float) -> None: ...
    def init(self) -> None: ...
    def initFlowCalc(self) -> None: ...
    def updateMolarFlow(self) -> None: ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("jneqsim.neqsim.fluidmechanics.flownode.onephasenode")``.

    onePhaseFlowNode: typing.Type[onePhaseFlowNode]
    onephasepipeflownode: jneqsim.neqsim.fluidmechanics.flownode.onephasenode.onephasepipeflownode.__module_protocol__
