
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import jneqsim.neqsim.statistics.experimentalequipmentdata
import jneqsim.neqsim.statistics.experimentalsamplecreation.samplecreator.wettedwallcolumnsamplecreator
import jneqsim.neqsim.thermo.system
import jneqsim.neqsim.thermodynamicoperations
import typing



class SampleCreator:
    @typing.overload
    def __init__(self): ...
    @typing.overload
    def __init__(self, systemInterface: jneqsim.neqsim.thermo.system.SystemInterface, thermodynamicOperations: jneqsim.neqsim.thermodynamicoperations.ThermodynamicOperations): ...
    def setExperimentalEquipment(self, experimentalEquipmentData: jneqsim.neqsim.statistics.experimentalequipmentdata.ExperimentalEquipmentData) -> None: ...
    def setThermoSystem(self, systemInterface: jneqsim.neqsim.thermo.system.SystemInterface) -> None: ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("jneqsim.neqsim.statistics.experimentalsamplecreation.samplecreator")``.

    SampleCreator: typing.Type[SampleCreator]
    wettedwallcolumnsamplecreator: jneqsim.neqsim.statistics.experimentalsamplecreation.samplecreator.wettedwallcolumnsamplecreator.__module_protocol__
