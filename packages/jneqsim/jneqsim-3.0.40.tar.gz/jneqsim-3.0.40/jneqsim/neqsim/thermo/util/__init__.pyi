
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import jneqsim.neqsim.thermo.util.Vega
import jneqsim.neqsim.thermo.util.benchmark
import jneqsim.neqsim.thermo.util.constants
import jneqsim.neqsim.thermo.util.empiric
import jneqsim.neqsim.thermo.util.gerg
import jneqsim.neqsim.thermo.util.humidair
import jneqsim.neqsim.thermo.util.jni
import jneqsim.neqsim.thermo.util.leachman
import jneqsim.neqsim.thermo.util.readwrite
import jneqsim.neqsim.thermo.util.referenceequations
import jneqsim.neqsim.thermo.util.steam
import typing


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("jneqsim.neqsim.thermo.util")``.

    Vega: jneqsim.neqsim.thermo.util.Vega.__module_protocol__
    benchmark: jneqsim.neqsim.thermo.util.benchmark.__module_protocol__
    constants: jneqsim.neqsim.thermo.util.constants.__module_protocol__
    empiric: jneqsim.neqsim.thermo.util.empiric.__module_protocol__
    gerg: jneqsim.neqsim.thermo.util.gerg.__module_protocol__
    humidair: jneqsim.neqsim.thermo.util.humidair.__module_protocol__
    jni: jneqsim.neqsim.thermo.util.jni.__module_protocol__
    leachman: jneqsim.neqsim.thermo.util.leachman.__module_protocol__
    readwrite: jneqsim.neqsim.thermo.util.readwrite.__module_protocol__
    referenceequations: jneqsim.neqsim.thermo.util.referenceequations.__module_protocol__
    steam: jneqsim.neqsim.thermo.util.steam.__module_protocol__
