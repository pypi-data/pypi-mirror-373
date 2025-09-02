
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import jneqsim.neqsim.fluidmechanics.flowleg
import jneqsim.neqsim.fluidmechanics.flownode
import jneqsim.neqsim.fluidmechanics.flowsolver
import jneqsim.neqsim.fluidmechanics.flowsystem
import jneqsim.neqsim.fluidmechanics.geometrydefinitions
import jneqsim.neqsim.fluidmechanics.util
import typing



class FluidMech:
    def __init__(self): ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("jneqsim.neqsim.fluidmechanics")``.

    FluidMech: typing.Type[FluidMech]
    flowleg: jneqsim.neqsim.fluidmechanics.flowleg.__module_protocol__
    flownode: jneqsim.neqsim.fluidmechanics.flownode.__module_protocol__
    flowsolver: jneqsim.neqsim.fluidmechanics.flowsolver.__module_protocol__
    flowsystem: jneqsim.neqsim.fluidmechanics.flowsystem.__module_protocol__
    geometrydefinitions: jneqsim.neqsim.fluidmechanics.geometrydefinitions.__module_protocol__
    util: jneqsim.neqsim.fluidmechanics.util.__module_protocol__
