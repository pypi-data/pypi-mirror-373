
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import jneqsim.neqsim.statistics.dataanalysis
import jneqsim.neqsim.statistics.experimentalequipmentdata
import jneqsim.neqsim.statistics.experimentalsamplecreation
import jneqsim.neqsim.statistics.montecarlosimulation
import jneqsim.neqsim.statistics.parameterfitting
import typing


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("jneqsim.neqsim.statistics")``.

    dataanalysis: jneqsim.neqsim.statistics.dataanalysis.__module_protocol__
    experimentalequipmentdata: jneqsim.neqsim.statistics.experimentalequipmentdata.__module_protocol__
    experimentalsamplecreation: jneqsim.neqsim.statistics.experimentalsamplecreation.__module_protocol__
    montecarlosimulation: jneqsim.neqsim.statistics.montecarlosimulation.__module_protocol__
    parameterfitting: jneqsim.neqsim.statistics.parameterfitting.__module_protocol__
