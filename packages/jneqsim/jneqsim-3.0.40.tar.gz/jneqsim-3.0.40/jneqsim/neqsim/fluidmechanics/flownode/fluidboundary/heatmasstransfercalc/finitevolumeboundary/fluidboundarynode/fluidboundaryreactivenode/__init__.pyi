
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import jneqsim.neqsim.fluidmechanics.flownode.fluidboundary.heatmasstransfercalc.finitevolumeboundary.fluidboundarynode
import jneqsim.neqsim.thermo.system
import typing



class FluidBoundaryNodeReactive(jneqsim.neqsim.fluidmechanics.flownode.fluidboundary.heatmasstransfercalc.finitevolumeboundary.fluidboundarynode.FluidBoundaryNode):
    @typing.overload
    def __init__(self): ...
    @typing.overload
    def __init__(self, systemInterface: jneqsim.neqsim.thermo.system.SystemInterface): ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("jneqsim.neqsim.fluidmechanics.flownode.fluidboundary.heatmasstransfercalc.finitevolumeboundary.fluidboundarynode.fluidboundaryreactivenode")``.

    FluidBoundaryNodeReactive: typing.Type[FluidBoundaryNodeReactive]
