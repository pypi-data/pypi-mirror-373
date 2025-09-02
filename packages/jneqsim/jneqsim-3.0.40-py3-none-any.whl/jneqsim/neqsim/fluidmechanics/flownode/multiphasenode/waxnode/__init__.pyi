
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import java.lang
import jpype
import jneqsim.neqsim.fluidmechanics.flownode
import jneqsim.neqsim.fluidmechanics.flownode.multiphasenode
import jneqsim.neqsim.fluidmechanics.flownode.twophasenode.twophasepipeflownode
import jneqsim.neqsim.fluidmechanics.geometrydefinitions
import jneqsim.neqsim.thermo.system
import typing



class WaxDepositionFlowNode(jneqsim.neqsim.fluidmechanics.flownode.multiphasenode.MultiPhaseFlowNode):
    @typing.overload
    def __init__(self): ...
    @typing.overload
    def __init__(self, systemInterface: jneqsim.neqsim.thermo.system.SystemInterface, geometryDefinitionInterface: jneqsim.neqsim.fluidmechanics.geometrydefinitions.GeometryDefinitionInterface): ...
    @typing.overload
    def __init__(self, systemInterface: jneqsim.neqsim.thermo.system.SystemInterface, systemInterface2: jneqsim.neqsim.thermo.system.SystemInterface, geometryDefinitionInterface: jneqsim.neqsim.fluidmechanics.geometrydefinitions.GeometryDefinitionInterface): ...
    def calcContactLength(self) -> float: ...
    def clone(self) -> jneqsim.neqsim.fluidmechanics.flownode.twophasenode.twophasepipeflownode.StratifiedFlowNode: ...
    def getNextNode(self) -> jneqsim.neqsim.fluidmechanics.flownode.FlowNodeInterface: ...
    def init(self) -> None: ...
    @staticmethod
    def main(stringArray: typing.Union[typing.List[java.lang.String], jpype.JArray]) -> None: ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("jneqsim.neqsim.fluidmechanics.flownode.multiphasenode.waxnode")``.

    WaxDepositionFlowNode: typing.Type[WaxDepositionFlowNode]
