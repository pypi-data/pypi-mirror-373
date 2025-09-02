
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import jneqsim.neqsim.fluidmechanics.flownode
import jneqsim.neqsim.fluidmechanics.util.fluidmechanicsvisualization.flownodevisualization.onephaseflownodevisualization
import typing



class OnePhasePipeFlowNodeVisualization(jneqsim.neqsim.fluidmechanics.util.fluidmechanicsvisualization.flownodevisualization.onephaseflownodevisualization.OnePhaseFlowNodeVisualization):
    def __init__(self): ...
    def setData(self, flowNodeInterface: jneqsim.neqsim.fluidmechanics.flownode.FlowNodeInterface) -> None: ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("jneqsim.neqsim.fluidmechanics.util.fluidmechanicsvisualization.flownodevisualization.onephaseflownodevisualization.onephasepipeflownodevisualization")``.

    OnePhasePipeFlowNodeVisualization: typing.Type[OnePhasePipeFlowNodeVisualization]
