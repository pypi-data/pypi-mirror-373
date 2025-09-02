
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import jneqsim.neqsim.api
import jneqsim.neqsim.blackoil
import jneqsim.neqsim.chemicalreactions
import jneqsim.neqsim.datapresentation
import jneqsim.neqsim.fluidmechanics
import jneqsim.neqsim.mathlib
import jneqsim.neqsim.physicalproperties
import jneqsim.neqsim.process
import jneqsim.neqsim.pvtsimulation
import jneqsim.neqsim.standards
import jneqsim.neqsim.statistics
import jneqsim.neqsim.thermo
import jneqsim.neqsim.thermodynamicoperations
import jneqsim.neqsim.util
import typing


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("jneqsim.neqsim.)``.

    api: jneqsim.neqsim.api.__module_protocol__
    blackoil: jneqsim.neqsim.blackoil.__module_protocol__
    chemicalreactions: jneqsim.neqsim.chemicalreactions.__module_protocol__
    datapresentation: jneqsim.neqsim.datapresentation.__module_protocol__
    fluidmechanics: jneqsim.neqsim.fluidmechanics.__module_protocol__
    mathlib: jneqsim.neqsim.mathlib.__module_protocol__
    physicalproperties: jneqsim.neqsim.physicalproperties.__module_protocol__
    process: jneqsim.neqsim.process.__module_protocol__
    pvtsimulation: jneqsim.neqsim.pvtsimulation.__module_protocol__
    standards: jneqsim.neqsim.standards.__module_protocol__
    statistics: jneqsim.neqsim.statistics.__module_protocol__
    thermo: jneqsim.neqsim.thermo.__module_protocol__
    thermodynamicoperations: jneqsim.neqsim.thermodynamicoperations.__module_protocol__
    util: jneqsim.neqsim.util.__module_protocol__
