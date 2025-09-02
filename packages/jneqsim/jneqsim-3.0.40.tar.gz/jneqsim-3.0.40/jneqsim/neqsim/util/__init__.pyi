
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import java.io
import java.lang
import java.lang.annotation
import jneqsim.neqsim.util.database
import jneqsim.neqsim.util.exception
import jneqsim.neqsim.util.generator
import jneqsim.neqsim.util.serialization
import jneqsim.neqsim.util.unit
import jneqsim.neqsim.util.util
import typing



class ExcludeFromJacocoGeneratedReport(java.lang.annotation.Annotation):
    def equals(self, object: typing.Any) -> bool: ...
    def hashCode(self) -> int: ...
    def toString(self) -> java.lang.String: ...

class NamedInterface:
    def getName(self) -> java.lang.String: ...
    def getTagName(self) -> java.lang.String: ...
    def setName(self, string: typing.Union[java.lang.String, str]) -> None: ...
    def setTagName(self, string: typing.Union[java.lang.String, str]) -> None: ...

class NeqSimLogging:
    def __init__(self): ...
    @staticmethod
    def resetAllLoggers() -> None: ...
    @staticmethod
    def setGlobalLogging(string: typing.Union[java.lang.String, str]) -> None: ...

class NamedBaseClass(NamedInterface, java.io.Serializable):
    name: java.lang.String = ...
    def __init__(self, string: typing.Union[java.lang.String, str]): ...
    def getName(self) -> java.lang.String: ...
    def getTagName(self) -> java.lang.String: ...
    def setName(self, string: typing.Union[java.lang.String, str]) -> None: ...
    def setTagName(self, string: typing.Union[java.lang.String, str]) -> None: ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("jneqsim.neqsim.util")``.

    ExcludeFromJacocoGeneratedReport: typing.Type[ExcludeFromJacocoGeneratedReport]
    NamedBaseClass: typing.Type[NamedBaseClass]
    NamedInterface: typing.Type[NamedInterface]
    NeqSimLogging: typing.Type[NeqSimLogging]
    database: jneqsim.neqsim.util.database.__module_protocol__
    exception: jneqsim.neqsim.util.exception.__module_protocol__
    generator: jneqsim.neqsim.util.generator.__module_protocol__
    serialization: jneqsim.neqsim.util.serialization.__module_protocol__
    unit: jneqsim.neqsim.util.unit.__module_protocol__
    util: jneqsim.neqsim.util.util.__module_protocol__
