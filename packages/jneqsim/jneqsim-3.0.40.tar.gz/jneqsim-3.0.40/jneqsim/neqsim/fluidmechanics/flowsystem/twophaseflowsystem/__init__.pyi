
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import jneqsim.neqsim.fluidmechanics.flowsystem
import jneqsim.neqsim.fluidmechanics.flowsystem.twophaseflowsystem.shipsystem
import jneqsim.neqsim.fluidmechanics.flowsystem.twophaseflowsystem.stirredcellsystem
import jneqsim.neqsim.fluidmechanics.flowsystem.twophaseflowsystem.twophasepipeflowsystem
import jneqsim.neqsim.fluidmechanics.flowsystem.twophaseflowsystem.twophasereactorflowsystem
import jneqsim.neqsim.fluidmechanics.geometrydefinitions.pipe
import jneqsim.neqsim.thermo.system
import typing



class TwoPhaseFlowSystem(jneqsim.neqsim.fluidmechanics.flowsystem.FlowSystem):
    pipe: jneqsim.neqsim.fluidmechanics.geometrydefinitions.pipe.PipeData = ...
    @typing.overload
    def __init__(self): ...
    @typing.overload
    def __init__(self, systemInterface: jneqsim.neqsim.thermo.system.SystemInterface): ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("jneqsim.neqsim.fluidmechanics.flowsystem.twophaseflowsystem")``.

    TwoPhaseFlowSystem: typing.Type[TwoPhaseFlowSystem]
    shipsystem: jneqsim.neqsim.fluidmechanics.flowsystem.twophaseflowsystem.shipsystem.__module_protocol__
    stirredcellsystem: jneqsim.neqsim.fluidmechanics.flowsystem.twophaseflowsystem.stirredcellsystem.__module_protocol__
    twophasepipeflowsystem: jneqsim.neqsim.fluidmechanics.flowsystem.twophaseflowsystem.twophasepipeflowsystem.__module_protocol__
    twophasereactorflowsystem: jneqsim.neqsim.fluidmechanics.flowsystem.twophaseflowsystem.twophasereactorflowsystem.__module_protocol__
