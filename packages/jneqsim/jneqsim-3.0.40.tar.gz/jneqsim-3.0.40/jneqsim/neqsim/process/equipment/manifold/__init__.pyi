
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import java.lang
import java.util
import jpype
import jneqsim.neqsim.process.equipment
import jneqsim.neqsim.process.equipment.stream
import jneqsim.neqsim.process.util.report
import typing



class Manifold(jneqsim.neqsim.process.equipment.ProcessEquipmentBaseClass):
    def __init__(self, string: typing.Union[java.lang.String, str]): ...
    def addStream(self, streamInterface: jneqsim.neqsim.process.equipment.stream.StreamInterface) -> None: ...
    def getMixedStream(self) -> jneqsim.neqsim.process.equipment.stream.StreamInterface: ...
    def getNumberOfOutputStreams(self) -> int: ...
    def getSplitStream(self, int: int) -> jneqsim.neqsim.process.equipment.stream.StreamInterface: ...
    @typing.overload
    def run(self) -> None: ...
    @typing.overload
    def run(self, uUID: java.util.UUID) -> None: ...
    def setName(self, string: typing.Union[java.lang.String, str]) -> None: ...
    def setSplitFactors(self, doubleArray: typing.Union[typing.List[float], jpype.JArray]) -> None: ...
    @typing.overload
    def toJson(self) -> java.lang.String: ...
    @typing.overload
    def toJson(self, reportConfig: jneqsim.neqsim.process.util.report.ReportConfig) -> java.lang.String: ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("jneqsim.neqsim.process.equipment.manifold")``.

    Manifold: typing.Type[Manifold]
