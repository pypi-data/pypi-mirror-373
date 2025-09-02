
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import jneqsim.neqsim.fluidmechanics.flowleg
import jneqsim.neqsim.fluidmechanics.flownode
import typing



class PipeLeg(jneqsim.neqsim.fluidmechanics.flowleg.FlowLeg):
    def __init__(self): ...
    @typing.overload
    def createFlowNodes(self) -> None: ...
    @typing.overload
    def createFlowNodes(self, flowNodeInterface: jneqsim.neqsim.fluidmechanics.flownode.FlowNodeInterface) -> None: ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("jneqsim.neqsim.fluidmechanics.flowleg.pipeleg")``.

    PipeLeg: typing.Type[PipeLeg]
