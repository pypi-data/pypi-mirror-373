from __future__ import annotations

from contextlib import AbstractContextManager, nullcontext

import pytest
from eksma_optics_motorized_devices.command import (
    AbstractCommand,
    BEXError,
    CommonCommand,
    Configuration,
    ConfigurationCollimation,
    ConfigurationMagnification,
    ConfigurationWavelength,
    FloatInfinityError,
    Identification,
    IdentificationValue,
    InstrumentControlCommand,
    Lens1,
    Lens2,
    NoQueryError,
    Preset,
    PresetDelete,
    PresetRemaining,
    PresetSave,
    QueryOnlyError,
    Reset,
    System,
    SystemBaudrate,
    SystemCollimationRange,
    SystemErr,
    SystemFlags,
    SystemFlagsValue,
    SystemHome,
    SystemMagnificationRange,
    SystemMinimalSpace,
    SystemStatus,
    SystemStatusValue,
    SystemVersion,
    SystemWavelenghts,
)
from eksma_optics_motorized_devices.decimal_with_dimension import DecimalWithDimension


def test_abstract_command_class() -> None:
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        AbstractCommand()  # type: ignore[abstract]


def test_abstract_command_parse_command_response() -> None:
    assert AbstractCommand.parse_command_response("some") == "some"


def test_abstract_command_parse_query_response() -> None:
    assert AbstractCommand.parse_query_response("some") == "some"


def test_common_command_class() -> None:
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        CommonCommand()  # type: ignore[abstract]


def test_instrument_control_command_class() -> None:
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        InstrumentControlCommand()  # type: ignore[abstract]


basic_command_and_query_testdata = [
    (
        Identification,
        pytest.raises(QueryOnlyError),
        nullcontext("*IDN?\r\n"),
    ),
    (
        Reset,
        nullcontext("*RST\r\n"),
        pytest.raises(NoQueryError),
    ),
    (
        Lens1,
        pytest.raises(TypeError),
        nullcontext(":LENS1?\r\n"),
    ),
    (
        Lens2,
        pytest.raises(TypeError),
        nullcontext(":LENS2?\r\n"),
    ),
    (
        Configuration,
        nullcontext(":CONF\r\n"),
        nullcontext(":CONF?\r\n"),
    ),
    (
        ConfigurationWavelength,
        pytest.raises(TypeError),
        nullcontext(":CONF:WAVE?\r\n"),
    ),
    (
        ConfigurationMagnification,
        pytest.raises(TypeError),
        nullcontext(":CONF:MAG?\r\n"),
    ),
    (
        ConfigurationCollimation,
        pytest.raises(TypeError),
        nullcontext(":CONF:COL?\r\n"),
    ),
    (
        Preset,
        pytest.raises(QueryOnlyError),
        nullcontext(":PRES?\r\n"),
    ),
    (
        PresetRemaining,
        pytest.raises(QueryOnlyError),
        nullcontext(":PRES:REM?\r\n"),
    ),
    (
        PresetSave,
        nullcontext(":PRES:SAVE\r\n"),
        pytest.raises(NoQueryError),
    ),
    (
        PresetDelete,
        pytest.raises(TypeError),
        pytest.raises(NoQueryError),
    ),
    (
        System,
        nullcontext(":SYST\r\n"),
        nullcontext(":SYST?\r\n"),
    ),
    (
        SystemWavelenghts,
        nullcontext(":SYST:WAVES\r\n"),
        nullcontext(":SYST:WAVES?\r\n"),
    ),
    (
        SystemMagnificationRange,
        nullcontext(":SYST:MAGR\r\n"),
        nullcontext(":SYST:MAGR?\r\n"),
    ),
    (
        SystemCollimationRange,
        nullcontext(":SYST:COLR\r\n"),
        nullcontext(":SYST:COLR?\r\n"),
    ),
    (
        SystemMinimalSpace,
        nullcontext(":SYST:MINS\r\n"),
        nullcontext(":SYST:MINS?\r\n"),
    ),
    (
        SystemHome,
        nullcontext(":SYST:HOME\r\n"),
        pytest.raises(NoQueryError),
    ),
    (
        SystemStatus,
        nullcontext(":SYST:STAT\r\n"),
        nullcontext(":SYST:STAT?\r\n"),
    ),
    (
        SystemErr,
        nullcontext(":SYST:ERR\r\n"),
        nullcontext(":SYST:ERR?\r\n"),
    ),
    (
        SystemVersion,
        pytest.raises(QueryOnlyError),
        nullcontext(":SYST:VERS?\r\n"),
    ),
    (
        SystemBaudrate,
        pytest.raises(TypeError),
        nullcontext(":SYST:BAUD?\r\n"),
    ),
    (
        SystemFlags,
        pytest.raises(QueryOnlyError),
        nullcontext(":SYST:FLAGS?\r\n"),
    ),
]


@pytest.mark.parametrize(("klass", "command", "query"), basic_command_and_query_testdata)
def test_basic_command_and_query(
    klass: type[AbstractCommand],
    command: AbstractContextManager,
    query: AbstractContextManager,
) -> None:
    cmd = klass()

    with command as c:
        assert cmd.command() == c

    with query as q:
        assert cmd.query() == q


command_float_three_testdata = [
    (Lens1, ":LENS1"),
    (Lens2, ":LENS2"),
]


@pytest.mark.parametrize(("klass", "prefix"), command_float_three_testdata)
def test_command_float_three(klass: type[AbstractCommand], prefix: str) -> None:
    cmd = klass()

    assert cmd.command(1) == f"{prefix} 1.000\r\n"
    assert cmd.command(0.1 + 0.2) == f"{prefix} 0.300\r\n"
    assert cmd.command(0.3) == f"{prefix} 0.300\r\n"
    assert cmd.command(-0.3) == f"{prefix} -0.300\r\n"

    with pytest.raises(FloatInfinityError):
        cmd.command(float("+inf"))
    with pytest.raises(FloatInfinityError):
        cmd.command(float("-inf"))


def test_configure_wave() -> None:
    prefix = ":CONF:WAVE"

    cmd = ConfigurationWavelength()

    assert cmd.command(1) == f"{prefix} 0001\r\n"
    assert cmd.command(9999) == f"{prefix} 9999\r\n"
    assert cmd.command(10000) == f"{prefix} 10000\r\n"


def test_configure_magnification() -> None:
    prefix = ":CONF:MAG"

    cmd = ConfigurationMagnification()

    assert cmd.command(1) == f"{prefix} 1.0\r\n"
    assert cmd.command(0.1 + 0.2) == f"{prefix} 0.3\r\n"
    assert cmd.command(0.3) == f"{prefix} 0.3\r\n"
    assert cmd.command(-0.3) == f"{prefix} -0.3\r\n"
    assert cmd.command(9999) == f"{prefix} 9999.0\r\n"
    assert cmd.command(10000) == f"{prefix} 10000.0\r\n"

    with pytest.raises(FloatInfinityError):
        cmd.command(float("+inf"))
    with pytest.raises(FloatInfinityError):
        cmd.command(float("-inf"))


def test_configure_collimation() -> None:
    prefix = ":CONF:COL"

    cmd = ConfigurationCollimation()

    assert cmd.command(1) == f"{prefix} 1\r\n"
    assert cmd.command(9999) == f"{prefix} 9999\r\n"
    assert cmd.command(10000) == f"{prefix} 10000\r\n"


def test_preset_parse_query_response() -> None:
    response = Preset.parse_query_response("")

    assert len(response) == 0

    response = Preset.parse_query_response("1,1.234,7;2,2.345,8;3,3.456,9")

    assert response[0].id == 1
    assert response[0].magnification == 1.234
    assert response[0].collimation == 7

    assert response[1].id == 2
    assert response[1].magnification == 2.345
    assert response[1].collimation == 8

    assert response[2].id == 3
    assert response[2].magnification == 3.456
    assert response[2].collimation == 9


def test_preset_delete() -> None:
    prefix = ":PRES:DEL"

    cmd = PresetDelete()

    assert cmd.command(0) == f"{prefix} 0\r\n"
    assert cmd.command(1) == f"{prefix} 1\r\n"


def test_identification_parse_query_response() -> None:
    response = Identification.parse_query_response("EKSMA Optics,M1,SN1,v1")

    assert isinstance(response, IdentificationValue)
    assert response.vendor == "EKSMA Optics"
    assert response.model == "M1"
    assert response.serial_number == "1"
    assert response.version == "1"

    assert response.description() == "EKSMA Optics M1 v1 (1)"

    with pytest.raises(ValueError, match="invalid identification response"):
        Identification.parse_query_response("invalid_response")

    with pytest.raises(ValueError, match="invalid serial number"):
        Identification.parse_query_response("EKSMA Optics,M1,invalid_serial_number,v1")

    with pytest.raises(ValueError, match="invalid version"):
        Identification.parse_query_response("EKSMA Optics,M1,SN1,invalid_version")


float_testdata = [
    (Lens1),
    (Lens2),
    (ConfigurationMagnification),
]


@pytest.mark.parametrize(("klass"), float_testdata)
def test_float_response(klass: AbstractCommand) -> None:
    with pytest.raises(ValueError, match="could not convert string to float"):
        assert klass.parse_query_response("not_a_number")
    assert klass.parse_query_response("-1.234") == -1.234
    assert klass.parse_query_response("1.234") == 1.234


int_testdata = [
    (ConfigurationCollimation),
    (PresetRemaining),
    (SystemBaudrate),
]


@pytest.mark.parametrize(("klass"), int_testdata)
def test_int_response(klass: AbstractCommand) -> None:
    with pytest.raises(ValueError, match="invalid literal for int\\(\\) with base 10"):
        assert klass.parse_query_response("not_a_number")
    assert klass.parse_query_response("10") == 10
    assert klass.parse_query_response("-10") == -10


value_with_dimension_testdata = [
    (ConfigurationWavelength),
    (SystemMinimalSpace),
]


@pytest.mark.parametrize(("klass"), value_with_dimension_testdata)
def test_value_with_dimension_response(klass: AbstractCommand) -> None:
    response = klass.parse_query_response("1234dim")

    assert isinstance(response, DecimalWithDimension)
    assert response.value == 1234
    assert response.dimension == "dim"


def test_system_wavelenghts_parse_query_response() -> None:
    with pytest.raises(ValueError, match="invalid format"):
        SystemWavelenghts.parse_query_response("invalid_value")

    response = SystemWavelenghts.parse_query_response("1nm,101nm,10002nm")

    assert len(response) == 3
    for i, res in enumerate(response):
        assert isinstance(res, DecimalWithDimension)
        assert res.value == (100**i) + i
        assert res.dimension == "nm"


def test_system_magnification_range_parse_query_response() -> None:
    with pytest.raises(ValueError, match="not enough values to unpack"):
        SystemMagnificationRange.parse_query_response("invalid_value")

    response = SystemMagnificationRange.parse_query_response("1,10")

    assert response == (1, 10)


def test_system_collimation_range_parse_query_response() -> None:
    with pytest.raises(ValueError, match="not enough values to unpack"):
        SystemCollimationRange.parse_query_response("invalid_value")

    response = SystemCollimationRange.parse_query_response("-10,10")

    assert response == (-10, 10)


def test_system_status_parse_query_response() -> None:
    invalid_value = "invalid_value"
    with pytest.raises(ValueError, match=f"'{invalid_value}' is not a valid"):
        SystemStatus.parse_query_response(invalid_value)

    response = SystemStatus.parse_query_response("Moving")

    assert response == SystemStatusValue.MOVING


def test_system_err_parse_query_response() -> None:
    no_error = "No Error"
    error = SystemErr.parse_query_response(no_error)
    assert error == no_error

    invalid_code = "invalid_code"
    error = SystemErr.parse_query_response(invalid_code)
    assert isinstance(error, BEXError)
    assert str(error) == f"{invalid_code}: unknown error"
    assert error.code == invalid_code

    code = "?c5"
    error = SystemErr.parse_query_response(code)
    assert isinstance(error, BEXError)
    assert str(error) == f"{code}: query only"
    assert error.code == code


def test_system_version_parse_query_response() -> None:
    with pytest.raises(ValueError, match="invalid version"):
        assert SystemVersion.parse_query_response("invalid_version")

    assert SystemVersion.parse_query_response("v1.1") == "1.1"


def test_system_baudrate() -> None:
    prefix = ":SYST:BAUD"

    cmd = SystemBaudrate()

    assert cmd.command(0) == f"{prefix} 0\r\n"
    assert cmd.command(1) == f"{prefix} 1\r\n"
    assert cmd.command(1.234) == f"{prefix} 1\r\n"
    assert cmd.command(3.234) == f"{prefix} 3\r\n"


def test_system_flags_parse_query_response() -> None:
    assert SystemFlags.parse_query_response("invalid_version") == SystemFlagsValue(0)

    assert SystemFlags.parse_query_response(5) == SystemFlagsValue(4) | SystemFlagsValue.STATE_CHANGED
