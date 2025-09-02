
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import jneqsim.neqsim.fluidmechanics.flowsystem
import jneqsim.neqsim.fluidmechanics.flowsystem.onephaseflowsystem.pipeflowsystem
import jneqsim.neqsim.fluidmechanics.geometrydefinitions.pipe
import jneqsim.neqsim.thermo.system
import typing



class OnePhaseFlowSystem(jneqsim.neqsim.fluidmechanics.flowsystem.FlowSystem):
    pipe: jneqsim.neqsim.fluidmechanics.geometrydefinitions.pipe.PipeData = ...
    @typing.overload
    def __init__(self): ...
    @typing.overload
    def __init__(self, systemInterface: jneqsim.neqsim.thermo.system.SystemInterface): ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("jneqsim.neqsim.fluidmechanics.flowsystem.onephaseflowsystem")``.

    OnePhaseFlowSystem: typing.Type[OnePhaseFlowSystem]
    pipeflowsystem: jneqsim.neqsim.fluidmechanics.flowsystem.onephaseflowsystem.pipeflowsystem.__module_protocol__
