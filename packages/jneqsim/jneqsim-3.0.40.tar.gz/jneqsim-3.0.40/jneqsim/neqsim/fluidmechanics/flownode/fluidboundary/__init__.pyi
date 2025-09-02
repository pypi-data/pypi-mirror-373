
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import jneqsim.neqsim.fluidmechanics.flownode.fluidboundary.heatmasstransfercalc
import jneqsim.neqsim.fluidmechanics.flownode.fluidboundary.interphasetransportcoefficient
import typing


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("jneqsim.neqsim.fluidmechanics.flownode.fluidboundary")``.

    heatmasstransfercalc: jneqsim.neqsim.fluidmechanics.flownode.fluidboundary.heatmasstransfercalc.__module_protocol__
    interphasetransportcoefficient: jneqsim.neqsim.fluidmechanics.flownode.fluidboundary.interphasetransportcoefficient.__module_protocol__
