from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, IntFlag, auto
from types import MappingProxyType
from typing import TYPE_CHECKING, Any

from eksma_optics_motorized_devices.decimal_with_dimension import DecimalWithDimension

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Iterable

LINE_ENDING = "\r\n"


class NoQueryError(Exception):
    def __init__(self) -> None:
        super().__init__("only command form is available")


class QueryOnlyError(Exception):
    def __init__(self) -> None:
        super().__init__("only query form is available")


class FloatInfinityError(ValueError):
    def __init__(self) -> None:
        super().__init__("float infinity is not supported")


class BEXError(Exception):
    ERROR_CODES = MappingProxyType(
        {
            "?m1": "short to ground indicator phase B",
            "?m2": "short to ground indicator phase A",
            "?m3": "open load indicator phase B",
            "?m4": "open load indicator phase A",
            "?m5": "overtemperature flag",
            "?m6": "short to supply indicator phase B",
            "?m7": "short to supply indicator phase A",
            "?p1": "Lens1 position error",
            "?p2": "Lens2 position error",
            "?c1": "first symbol mismatch",
            "?c2": "command not found",
            "?c3": "value mismatch",
            "?c4": "value limit exceed",
            "?c5": "query only",
        },
    )

    def __init__(self, code: str) -> None:
        self.code = code
        message = self.ERROR_CODES.get(code, "unknown error")
        full_message = f"{code}: {message}"

        super().__init__(full_message)


class AbstractCommand(ABC):
    """
    Base class for all command classes.

    This class provides two methods for rendering the command string:

    - :meth:`.command()` for actionable form.
    - :meth:`.query()` for query form.
    """

    no_query = False
    query_only = False
    parent: type[AbstractCommand] | None = None

    @staticmethod
    def parse_command_response(value: str) -> Any:  # noqa: ANN401
        return value

    @staticmethod
    def parse_query_response(value: str) -> Any:  # noqa: ANN401
        return value

    @abstractmethod
    def mnemonic(self) -> str:
        pass  # pragma: no cover

    @abstractmethod
    def _command_header(self) -> str:
        pass  # pragma: no cover

    def _query_header(self) -> str:
        return f"{self._command_header()}?"

    def command(self, *args: Any) -> str:  # noqa: ANN401
        if self.query_only:
            raise QueryOnlyError

        return self._format(self._command_header(), *args)

    def query(self, *args: Any) -> str:  # noqa: ANN401
        if self.no_query:
            raise NoQueryError

        return self._format(self._query_header(), *args)

    def _format(self, header: str, *args: tuple[Any]) -> str:
        out = header

        if len(args) > 0:
            out += f" {','.join([str(a) for a in args])}"

        out += LINE_ENDING

        return out


class CommonCommand(AbstractCommand):
    """
    Base class for common command classes.

    Commands of this type are prefixed with ``*``.
    """

    def _command_header(self) -> str:
        return f"*{self.mnemonic()}"


class InstrumentControlCommand(AbstractCommand):
    """
    Base class for instrument control command classes.

    These commands are prefixed, and command chains are joined with ``:``.
    """

    def _command_header(self) -> str:
        mnemonics = self._fully_qualified_mnemonic()

        return f":{':'.join(mnemonics)}"

    def _fully_qualified_mnemonic(self) -> Iterable[str]:
        parts: list[str] = []
        parent: type[AbstractCommand] | None = self.__class__
        while parent is not None:
            instance = parent()
            parts.append(instance.mnemonic())
            parent = instance.parent

        return reversed(parts)


@dataclass
class IdentificationValue:
    vendor: str
    model: str
    serial_number: str
    version: str
    raw: str

    def description(self) -> str:
        return f"{self.vendor} {self.model} v{self.version} ({self.serial_number})"


class Identification(CommonCommand):
    """
    Device identification query.

    Response:

    - identification: ``manufacturer_name,device_model,serial_number,firmware_version``

    Example::

      > *IDN?
      < EKSMA Optics,BEX,SN0,v01

    """

    def __init__(self) -> None:
        self.query_only = True

    @classmethod
    def parse_query_response(cls, value: str) -> IdentificationValue:
        try:
            vendor, model, serial_number, version = value.split(",")
        except ValueError as ex:
            msg = "invalid identification response"
            raise ValueError(msg) from ex

        if (serial_number_match := re.match("^SN(.+)$", serial_number)) is None:
            msg = "invalid serial number"
            raise ValueError(msg)

        serial_number = serial_number_match.group(1)
        version = SystemVersion.parse_query_response(version)

        return IdentificationValue(vendor=vendor, model=model, serial_number=serial_number, version=version, raw=value)

    def mnemonic(self) -> str:
        return "IDN"


class Reset(CommonCommand):
    """
    Command resets the device to its default state.

    Example::

      > *RST
      < OK

    """

    def __init__(self) -> None:
        self.no_query = True

    def mnemonic(self) -> str:
        return "RST"


class Lens1(InstrumentControlCommand):
    r"""
    Command moves magnification lens to absolute position in milimeters.

    Query returns the current absolute position of the lens in millimeters.

    Parameters\:

    - position: ``float``

    Response:

    - position: ``float``

    Example::

      > :LENS1 10.001
      < OK

      > :LENS1?
      < 10.001

    """

    @classmethod
    def parse_query_response(cls, value: str) -> float:
        return float(value)

    def mnemonic(self) -> str:
        return "LENS1"

    def command(self, value: float) -> str:
        return InstrumentControlCommand.command(self, _format_dot_three_f(value))


class Lens2(InstrumentControlCommand):
    r"""
    Command moves collimation lens to absolute position in milimeters.

    Query returns the current absolute position of the lens in millimeters.

    Parameters\:

    - position: ``float``

    Response:

    - position: ``float``

    Example::

      > :LENS2 20.001
      < OK

      > :LENS2
      < 20.001

    """

    @classmethod
    def parse_query_response(cls, value: str) -> float:
        return float(value)

    def mnemonic(self) -> str:
        return "LENS2"

    def command(self, value: float) -> str:
        return InstrumentControlCommand.command(self, _format_dot_three_f(value))


class Configuration(InstrumentControlCommand):
    def mnemonic(self) -> str:
        return "CONF"


class ConfigurationWavelength(InstrumentControlCommand):
    r"""
    Command sets the operating wavelength in nanometers.

    Query returns the operating wavelength.

    Parameters\:

    - wavelength: ``int``

    Response:

    - position: ``int`` nm

    Example::

      > :CONF:WAVE 515
      < OK

      > :CONF:WAVE?
      < 515nm

    """

    parent = Configuration

    @classmethod
    def parse_query_response(cls, value: str) -> DecimalWithDimension:
        return DecimalWithDimension.from_string(value)

    def mnemonic(self) -> str:
        return "WAVE"

    def command(self, wavelength: int) -> str:
        return InstrumentControlCommand.command(self, _format_zero_four_u(wavelength))


class ConfigurationMagnification(InstrumentControlCommand):
    r"""
    Command sets the magnification factor.

    Query returns the magnification factor.

    Parameters\:

    - magnification: ``float``

    Response:

    - magnification: ``float``

    Example::

      > :CONF:MAG 4.5
      < OK

      > :CONF:MAG?
      < 4.50

    """

    parent = Configuration

    @classmethod
    def parse_query_response(cls, value: str) -> float:
        return float(value)

    def mnemonic(self) -> str:
        return "MAG"

    def command(self, magnification: float) -> str:
        return InstrumentControlCommand.command(self, _format_dot_one_f(magnification))


class ConfigurationCollimation(InstrumentControlCommand):
    r"""
    Command sets the collimation setting.

    Query returns the collimation setting.

    Parameters\:

    - collimation: ``int``

    Response:

    - collimation: ``int``

    Example::

      > :CONF:COL 3
      < OK

      > :CONF:COL?
      < 3

    """

    parent = Configuration

    @classmethod
    def parse_query_response(cls, value: str) -> int:
        return int(value)

    def mnemonic(self) -> str:
        return "COL"

    def command(self, collimation: int) -> str:
        return InstrumentControlCommand.command(self, _format_d(collimation))


@dataclass
class PresetValue:
    id: int
    magnification: float
    collimation: int


class Preset(InstrumentControlCommand):
    r"""
    Query returns all stored configuration presets.

    Presets are semicolon separated and preset fields are commma separated.

    Response:

    - presets: ``[(preset_id: int,magnification: float,collimation: int)]``

    Flags are defined in :class:`PresetValue`.

    Example::

      > :PRES?
      < 1,1,0;2,2,0

    """

    @staticmethod
    def parse_query_response(value: str) -> list[PresetValue]:
        presets = value.split(";")

        out = []
        for preset in presets:
            if len(preset) == 0:
                break

            preset_id, mag, col = preset.split(",")

            out.append(PresetValue(id=int(preset_id), magnification=float(mag), collimation=int(col)))

        return out

    def __init__(self) -> None:
        self.query_only = True

    def mnemonic(self) -> str:
        return "PRES"


class PresetRemaining(InstrumentControlCommand):
    """
    Query returns the number of remaining preset slots available.

    Response:

    - remaining: ``int``

    Example::

      > :PRES:REM?
      < 10

    """

    parent = Preset

    def __init__(self) -> None:
        self.query_only = True

    @staticmethod
    def parse_query_response(value: str) -> int:
        return int(value)

    def mnemonic(self) -> str:
        return "REM"

    def command(self) -> str:
        return InstrumentControlCommand.command(self)


class PresetSave(InstrumentControlCommand):
    """
    Command saves the current configuration as a new preset.

    Example::

      > :PRES:SAVE
      < OK

    """

    parent = Preset

    def __init__(self) -> None:
        self.no_query = True

    def mnemonic(self) -> str:
        return "SAVE"

    def command(self) -> str:
        return InstrumentControlCommand.command(self)


class PresetDelete(InstrumentControlCommand):
    r"""
    Command deletes a preset by its index.

    Parameters\:

    - preset_id: ``int``

    Example::

      > :PRES:DEL 6
      < OK

    """

    parent = Preset

    def __init__(self) -> None:
        self.no_query = True

    def mnemonic(self) -> str:
        return "DEL"

    def command(self, preset_id: int) -> str:
        return InstrumentControlCommand.command(self, str(preset_id))


class System(InstrumentControlCommand):
    def mnemonic(self) -> str:
        return "SYST"


class SystemWavelenghts(InstrumentControlCommand):
    r"""
    Query returns the list of supported operational wavelengths.

    Response:

    - wavelengths: ``(wavelength0: int "nm", wavelength1: int "nm", ...)``

    Example::

      > :SYST:WAVES?
      < 1064nm,1030nm,800nm,532nm,515nm,355nm,343nm,266nm

    """

    parent = System

    @classmethod
    def parse_query_response(cls, value: str) -> list[DecimalWithDimension]:
        return [DecimalWithDimension.from_string(s) for s in value.split(",")]

    def mnemonic(self) -> str:
        return "WAVES"


class SystemMagnificationRange(InstrumentControlCommand):
    """
    Query return the supported range of magnification values.

    Response:

    - magnification_range: ``(min: float, max: float)``

    Example::

      > SYST:MAGR?
      < 1.0,5.0

    """

    parent = System

    @classmethod
    def parse_query_response(cls, value: str) -> tuple[float, float]:
        mag_min, mag_max = value.split(",")
        return float(mag_min.rstrip("x")), float(mag_max.rstrip("x"))

    def mnemonic(self) -> str:
        return "MAGR"


class SystemCollimationRange(InstrumentControlCommand):
    """
    Query returns the supported range of collimation values.

    Response:

    - collimation_range: ``(min: int, max: int)``

    Example::

      > SYST:COLR?
      < -10,10

    """

    parent = System

    @classmethod
    def parse_query_response(cls, value: str) -> tuple[int, int]:
        col_min, col_max = value.split(",")
        return int(col_min), int(col_max)

    def mnemonic(self) -> str:
        return "COLR"


class SystemMinimalSpace(InstrumentControlCommand):
    """
    Query returns the minimal space allowed between lenses.

    Response:

    - minimum_space: ``int`` mm

    Example::

      > SYST:MINS?
      < 10mm

    """

    parent = System

    @classmethod
    def parse_query_response(cls, value: str) -> DecimalWithDimension:
        return DecimalWithDimension.from_string(value)

    def mnemonic(self) -> str:
        return "MINS"


class SystemHome(InstrumentControlCommand):
    """
    Reset internal state and lense positions to the initial state.

    Example::

      > SYST:HOME
      < OK

    """

    parent = System

    def __init__(self) -> None:
        self.no_query = True

    def mnemonic(self) -> str:
        return "HOME"

    def command(self) -> str:
        return InstrumentControlCommand.command(self)


class SystemStatusValue(str, Enum):
    IDLE = "Idle"
    MOVING = "Moving"
    INITIALIZING = "initializing"
    ERROR = "Error"
    FATAL_ERROR = "Fatal Error"


class SystemStatus(InstrumentControlCommand):
    """
    Query returns the firmware version string of the device.

    Response:

    - wavelengths: ``str``

    Example::

      > SYST:STAT?
      < Idle

    """

    parent = System

    @classmethod
    def parse_query_response(cls, value: str) -> SystemStatusValue:
        return SystemStatusValue(value)

    def mnemonic(self) -> str:
        return "STAT"


class SystemErr(InstrumentControlCommand):
    """
    Query returns the last error reported by the device.

    Response:

    - error: ``str``

    Example::

      > SYST:ERR?
      < ?c4

    """

    parent = System

    NO_ERROR = "No Error"

    @classmethod
    def parse_query_response(cls, value: str) -> str | BEXError:
        if value == cls.NO_ERROR:
            return value

        return BEXError(value)

    def mnemonic(self) -> str:
        return "ERR"


class SystemVersion(InstrumentControlCommand):
    """
    Query returns the current firmware version.

    Response:

    - version: v ``str``

    Example::

      > SYST:VERS?
      < v01

    """

    parent = System

    @classmethod
    def parse_query_response(cls, value: str) -> str:
        if (match := re.match("^v(.+)$", value)) is None:
            msg = "invalid version"
            raise ValueError(msg)

        return match.group(1)

    def __init__(self) -> None:
        self.query_only = True

    def mnemonic(self) -> str:
        return "VERS"


class SystemBaudrate(InstrumentControlCommand):
    r"""
    Command sets the baud rate.

    Query returns the baud rate.

    Parameters\:

    - baudrate: ``int``

    Response:

    - baudrate: ``int``

    Example::

      > :SYST:BAUD 19200
      < OK

      > :SYST:BAUD?
      < 19200

    """

    parent = System

    @classmethod
    def parse_query_response(cls, value: str) -> int:
        return int(value)

    def mnemonic(self) -> str:
        return "BAUD"

    def command(self, baudrate: int) -> str:
        return InstrumentControlCommand.command(self, _format_d(baudrate))


class SystemFlagsValue(IntFlag):
    STATE_CHANGED = auto()


class SystemFlags(InstrumentControlCommand):
    """
    Query returns the system flags indicating current status.

    Example::

      > SYST:FLAGS?
      < 1

    """

    parent = System

    @classmethod
    def parse_query_response(cls, value: str) -> SystemFlagsValue:
        try:
            return SystemFlagsValue(int(value))
        except ValueError:
            return SystemFlagsValue(0)

    def __init__(self) -> None:
        self.query_only = True

    def mnemonic(self) -> str:
        return "FLAGS"


def _assert_float_finite(value: float) -> None:
    if value == float("+inf") or value == float("-inf"):
        raise FloatInfinityError


def _format_dot_three_f(value: float) -> str:
    value = float(value)
    _assert_float_finite(value)

    return f"{value:.3f}"


def _format_dot_one_f(value: float) -> str:
    value = float(value)
    _assert_float_finite(value)

    return f"{value:.1f}"


def _format_zero_four_u(value: int) -> str:
    return f"{int(value):04}"


def _format_d(value: int) -> str:
    return f"{int(value):d}"


def _format_tuple(value: tuple) -> str:
    return ",".join(str(v) for v in value)
