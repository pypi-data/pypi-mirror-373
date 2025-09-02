
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import jneqsim.neqsim.fluidmechanics.flownode.fluidboundary.heatmasstransfercalc.finitevolumeboundary.fluidboundarynode
import jneqsim.neqsim.fluidmechanics.flownode.fluidboundary.heatmasstransfercalc.finitevolumeboundary.fluidboundarysolver
import jneqsim.neqsim.fluidmechanics.flownode.fluidboundary.heatmasstransfercalc.finitevolumeboundary.fluidboundarysystem
import typing


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("jneqsim.neqsim.fluidmechanics.flownode.fluidboundary.heatmasstransfercalc.finitevolumeboundary")``.

    fluidboundarynode: jneqsim.neqsim.fluidmechanics.flownode.fluidboundary.heatmasstransfercalc.finitevolumeboundary.fluidboundarynode.__module_protocol__
    fluidboundarysolver: jneqsim.neqsim.fluidmechanics.flownode.fluidboundary.heatmasstransfercalc.finitevolumeboundary.fluidboundarysolver.__module_protocol__
    fluidboundarysystem: jneqsim.neqsim.fluidmechanics.flownode.fluidboundary.heatmasstransfercalc.finitevolumeboundary.fluidboundarysystem.__module_protocol__
