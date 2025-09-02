
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import jneqsim.neqsim.fluidmechanics.geometrydefinitions
import typing



class StirredCell(jneqsim.neqsim.fluidmechanics.geometrydefinitions.GeometryDefinition):
    @typing.overload
    def __init__(self): ...
    @typing.overload
    def __init__(self, double: float): ...
    @typing.overload
    def __init__(self, double: float, double2: float): ...
    def clone(self) -> 'StirredCell': ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("jneqsim.neqsim.fluidmechanics.geometrydefinitions.stirredcell")``.

    StirredCell: typing.Type[StirredCell]
