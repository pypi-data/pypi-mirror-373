
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import jneqsim.neqsim.process.util.monitor
import jneqsim.neqsim.process.util.report
import typing


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("jneqsim.neqsim.process.util")``.

    monitor: jneqsim.neqsim.process.util.monitor.__module_protocol__
    report: jneqsim.neqsim.process.util.report.__module_protocol__
