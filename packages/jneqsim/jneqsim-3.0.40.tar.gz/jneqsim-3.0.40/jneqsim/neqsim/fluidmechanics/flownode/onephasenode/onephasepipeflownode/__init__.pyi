
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import java.lang
import jpype
import jneqsim.neqsim.fluidmechanics.flownode.onephasenode
import jneqsim.neqsim.fluidmechanics.geometrydefinitions
import jneqsim.neqsim.thermo.system
import typing



class onePhasePipeFlowNode(jneqsim.neqsim.fluidmechanics.flownode.onephasenode.onePhaseFlowNode):
    @typing.overload
    def __init__(self): ...
    @typing.overload
    def __init__(self, systemInterface: jneqsim.neqsim.thermo.system.SystemInterface, geometryDefinitionInterface: jneqsim.neqsim.fluidmechanics.geometrydefinitions.GeometryDefinitionInterface): ...
    def calcReynoldsNumber(self) -> float: ...
    def clone(self) -> 'onePhasePipeFlowNode': ...
    @staticmethod
    def main(stringArray: typing.Union[typing.List[java.lang.String], jpype.JArray]) -> None: ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("jneqsim.neqsim.fluidmechanics.flownode.onephasenode.onephasepipeflownode")``.

    onePhasePipeFlowNode: typing.Type[onePhasePipeFlowNode]
