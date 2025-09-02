
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import jneqsim.neqsim.fluidmechanics.util.fluidmechanicsvisualization
import jneqsim.neqsim.fluidmechanics.util.timeseries
import typing


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("jneqsim.neqsim.fluidmechanics.util")``.

    fluidmechanicsvisualization: jneqsim.neqsim.fluidmechanics.util.fluidmechanicsvisualization.__module_protocol__
    timeseries: jneqsim.neqsim.fluidmechanics.util.timeseries.__module_protocol__
