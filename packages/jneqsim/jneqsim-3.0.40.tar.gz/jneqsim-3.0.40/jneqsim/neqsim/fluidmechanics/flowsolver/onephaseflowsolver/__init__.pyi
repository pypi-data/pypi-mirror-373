
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import jneqsim.neqsim.fluidmechanics.flowsolver
import jneqsim.neqsim.fluidmechanics.flowsolver.onephaseflowsolver.onephasepipeflowsolver
import typing



class OnePhaseFlowSolver(jneqsim.neqsim.fluidmechanics.flowsolver.FlowSolver):
    def __init__(self): ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("jneqsim.neqsim.fluidmechanics.flowsolver.onephaseflowsolver")``.

    OnePhaseFlowSolver: typing.Type[OnePhaseFlowSolver]
    onephasepipeflowsolver: jneqsim.neqsim.fluidmechanics.flowsolver.onephaseflowsolver.onephasepipeflowsolver.__module_protocol__
