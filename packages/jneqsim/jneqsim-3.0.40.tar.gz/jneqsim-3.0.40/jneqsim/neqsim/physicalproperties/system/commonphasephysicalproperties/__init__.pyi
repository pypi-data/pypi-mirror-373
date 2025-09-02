
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import jneqsim.neqsim.physicalproperties.system
import jneqsim.neqsim.thermo.phase
import typing



class DefaultPhysicalProperties(jneqsim.neqsim.physicalproperties.system.PhysicalProperties):
    def __init__(self, phaseInterface: jneqsim.neqsim.thermo.phase.PhaseInterface, int: int, int2: int): ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("jneqsim.neqsim.physicalproperties.system.commonphasephysicalproperties")``.

    DefaultPhysicalProperties: typing.Type[DefaultPhysicalProperties]
