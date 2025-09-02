
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import jneqsim.neqsim.fluidmechanics.util.fluidmechanicsvisualization.flownodevisualization
import jneqsim.neqsim.fluidmechanics.util.fluidmechanicsvisualization.flownodevisualization.onephaseflownodevisualization.onephasepipeflownodevisualization
import typing



class OnePhaseFlowNodeVisualization(jneqsim.neqsim.fluidmechanics.util.fluidmechanicsvisualization.flownodevisualization.FlowNodeVisualization):
    def __init__(self): ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("jneqsim.neqsim.fluidmechanics.util.fluidmechanicsvisualization.flownodevisualization.onephaseflownodevisualization")``.

    OnePhaseFlowNodeVisualization: typing.Type[OnePhaseFlowNodeVisualization]
    onephasepipeflownodevisualization: jneqsim.neqsim.fluidmechanics.util.fluidmechanicsvisualization.flownodevisualization.onephaseflownodevisualization.onephasepipeflownodevisualization.__module_protocol__
