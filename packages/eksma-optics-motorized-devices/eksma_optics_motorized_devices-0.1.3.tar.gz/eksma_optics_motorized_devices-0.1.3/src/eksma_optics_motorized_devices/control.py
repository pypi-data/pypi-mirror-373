from __future__ import annotations

import logging
import threading
import time
from contextlib import contextmanager
from typing import TYPE_CHECKING

from eksma_optics_motorized_devices.command import (
    LINE_ENDING,
    BEXError,
    ConfigurationCollimation,
    ConfigurationMagnification,
    ConfigurationWavelength,
    DecimalWithDimension,
    Identification,
    IdentificationValue,
    Lens1,
    Lens2,
    Preset,
    PresetDelete,
    PresetRemaining,
    PresetSave,
    PresetValue,
    Reset,
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

if TYPE_CHECKING:
    from collections.abc import Generator

    from eksma_optics_motorized_devices.transport import Transport

logger = logging.getLogger(__name__)


def _strip_nl(value: str) -> str:
    return value.rstrip(LINE_ENDING)


class DeviceTimeoutError(Exception):
    """Exception raised when a device fails to reach the expected state within a timeout."""


class Control:
    """
    High-level device controller for EKSMA motorized devices.

    Provides methods to read and set optical parameters, execute system commands, and
    manage presets. Thread-safe and designed for synchronous command-response operations.

    :param transport: The communication transport used to send and receive data.
    :type transport: Transport
    """

    STATUS_OK = "OK"
    TIMEOUT = 40

    @classmethod
    def _expect_ok(cls, value: str) -> None:
        if value != cls.STATUS_OK:
            raise BEXError(value)

    @contextmanager
    def _wait_for_status_idle(self) -> Generator[None, None, None]:
        try:
            yield
        finally:
            start_time = time.time()
            while True:
                current_time = time.time()
                status = self._get_status_unsafe()

                if status == SystemStatusValue.IDLE:
                    break

                if (current_time - start_time) >= self.TIMEOUT:
                    raise DeviceTimeoutError

    def __init__(self, transport: Transport) -> None:
        """
        Initialize the controller with the given transport.

        :param transport: An object implementing the Transport interface.
        :type transport: Transport
        """
        self._transport = transport

        self._lock = threading.Lock()

    def wait_for_status_idle(self) -> None:
        """
        Block until the device status becomes idle or a timeout occurs.

        This method waits for the device to reach the 'Idle' status. If the device does not
        become idle within the allowed time, a DeviceTimeoutError is raised.

        :raises DeviceTimeoutError: If the device fails to become idle before the timeout.
        """
        with self._wait_for_status_idle():
            pass

    def get_identification(self) -> IdentificationValue:
        """
        Get the device identification information.

        :return: Parsed identification value.
        :rtype: IdentificationValue
        """
        with self._lock:
            self._transport.write(Identification().query())
            response = _strip_nl(self._transport.read())

        return Identification.parse_query_response(response)

    def reset(self) -> None:
        """Reset the device."""
        with self._lock:
            self._transport.write(Reset().command())
            response = _strip_nl(self._transport.read())

        self._expect_ok(response)

    def get_lens1(self) -> float:
        """
        Get the position of Lens 1.

        :return: Position of Lens 1 in milimeters.
        :rtype: float
        """
        with self._lock:
            self._transport.write(Lens1().query())
            response = _strip_nl(self._transport.read())

        return Lens1.parse_query_response(response)

    def set_lens1_unsafe(self, value: float) -> None:
        """
        Set the position of Lens 1 without waiting for idle status.

        :param value: New position for Lens 1 in milimeters.
        :type value: float
        """
        self._transport.write(Lens1().command(value))
        response = _strip_nl(self._transport.read())

        self._expect_ok(response)

    def set_lens1(self, value: float) -> None:
        """
        Safely set the position of Lens 1, waiting for the device to be idle.

        :param value: New position for Lens 1 in milimeters.
        :type value: float
        """
        with self._lock, self._wait_for_status_idle():
            self.set_lens1_unsafe(value)

    def get_lens2(self) -> float:
        """
        Get the position of Lens 2.

        :return: Position of Lens 2 in milimeters.
        :rtype: float
        """
        with self._lock:
            self._transport.write(Lens2().query())
            response = _strip_nl(self._transport.read())

        return Lens2.parse_query_response(response)

    def set_lens2_unsafe(self, value: float) -> None:
        """
        Set the position of Lens 2 without waiting for idle status.

        :param value: New position for Lens 2 in milimeters.
        :type value: float
        """
        self._transport.write(Lens2().command(value))
        response = _strip_nl(self._transport.read())

        self._expect_ok(response)

    def set_lens2(self, value: float) -> None:
        """
        Safely set the position of Lens 2, waiting for the device to be idle.

        :param value: New position for Lens 2 in milimeters.
        :type value: float
        """
        with self._lock, self._wait_for_status_idle():
            self.set_lens2_unsafe(value)

    def get_wavelength(self) -> DecimalWithDimension:
        """
        Get the current wavelength setting of the device.

        :returns: Current wavelength with unit.
        :rtype: DecimalWithDimension
        """
        with self._lock:
            self._transport.write(ConfigurationWavelength().query())
            response = _strip_nl(self._transport.read())

        return ConfigurationWavelength.parse_query_response(response)

    def set_wavelength(self, value: int) -> None:
        """
        Set the operating wavelength of the device.

        :param value: Wavelength value in nanometers.
        :type value: int
        """
        with self._lock:
            self._transport.write(ConfigurationWavelength().command(value))
            response = _strip_nl(self._transport.read())

        self._expect_ok(response)

    def get_magnification(self) -> float:
        """
        Get the current magnification factor.

        :returns: Magnification factor.
        :rtype: float
        """
        with self._lock:
            self._transport.write(ConfigurationMagnification().query())
            response = _strip_nl(self._transport.read())

        return ConfigurationMagnification.parse_query_response(response)

    def set_magnification_unsafe(self, value: float) -> None:
        """
        Set the magnification factor without waiting for idle state.

        :param value: Desired magnification factor.
        :type value: float
        """
        self._transport.write(ConfigurationMagnification().command(value))
        response = _strip_nl(self._transport.read())

        self._expect_ok(response)

    def set_magnification(self, value: float) -> None:
        """
        Set the magnification factor, waiting for the device to be idle.

        :param value: Desired magnification factor.
        :type value: float
        """
        with self._lock, self._wait_for_status_idle():
            self.set_magnification_unsafe(value)

    def get_collimation(self) -> int:
        """
        Get the current collimation setting.

        :returns: Collimation value.
        :rtype: int
        """
        with self._lock:
            self._transport.write(ConfigurationCollimation().query())
            response = _strip_nl(self._transport.read())

        return ConfigurationCollimation.parse_query_response(response)

    def set_collimation_unsafe(self, value: int) -> None:
        """
        Set the collimation value without waiting for idle state.

        :param value: Desired collimation setting.
        :type value: int
        """
        self._transport.write(ConfigurationCollimation().command(value))
        response = _strip_nl(self._transport.read())

        self._expect_ok(response)

    def set_collimation(self, value: int) -> None:
        """
        Set the collimation value, waiting for the device to be idle.

        :param value: Desired collimation setting.
        :type value: int
        """
        with self._lock, self._wait_for_status_idle():
            self.set_collimation_unsafe(value)

    def get_presets(self) -> list[PresetValue]:
        """
        Get all stored configuration presets.

        :returns: List of preset values.
        :rtype: list[PresetValue]
        """
        with self._lock:
            self._transport.write(Preset().query())
            response = _strip_nl(self._transport.read())

        return Preset.parse_query_response(response)

    def save_preset(self) -> None:
        """Save the current configuration as a new preset."""
        with self._lock:
            self._transport.write(PresetSave().command())
            response = _strip_nl(self._transport.read())

        self._expect_ok(response)

    def get_remaining_presets(self) -> int:
        """
        Get the number of remaining preset slots available.

        :returns: Number of available preset slots.
        :rtype: int
        """
        with self._lock:
            self._transport.write(PresetRemaining().query())
            response = _strip_nl(self._transport.read())

        return PresetRemaining.parse_query_response(response)

    def delete_preset(self, value: int) -> None:
        """
        Delete a preset by its index.

        :param value: Index of the preset to delete.
        :type value: int
        """
        with self._lock:
            self._transport.write(PresetDelete().command(value))
            response = _strip_nl(self._transport.read())

        self._expect_ok(response)

    def get_wavelengths(self) -> list[DecimalWithDimension]:
        """
        Get the list of supported operational wavelengths.

        :returns: List of supported operational wavelengths.
        :rtype: list[DecimalWithDimension]
        """
        with self._lock:
            self._transport.write(SystemWavelenghts().query())
            response = _strip_nl(self._transport.read())

        return SystemWavelenghts.parse_query_response(response)

    def get_magnification_range(self) -> tuple[float, float]:
        """
        Get the supported range of magnification values.

        :returns: Tuple containing minimum and maximum magnification.
        :rtype: tuple[float, float]
        """
        with self._lock:
            self._transport.write(SystemMagnificationRange().query())
            response = _strip_nl(self._transport.read())

        return SystemMagnificationRange.parse_query_response(response)

    def get_collimation_range(self) -> tuple[int, int]:
        """
        Get the supported range of collimation values.

        :returns: Tuple containing minimum and maximum collimation.
        :rtype: tuple[int, int]
        """
        with self._lock:
            self._transport.write(SystemCollimationRange().query())
            response = _strip_nl(self._transport.read())

        return SystemCollimationRange.parse_query_response(response)

    def get_minimal_lens_space(self) -> DecimalWithDimension:
        """
        Get the minimal space allowed between lenses.

        :returns: Minimal lens space with unit.
        :rtype: DecimalWithDimension
        """
        with self._lock:
            self._transport.write(SystemMinimalSpace().query())
            response = _strip_nl(self._transport.read())

        return SystemMinimalSpace.parse_query_response(response)

    def home_unsafe(self) -> None:
        """Reset internal state and lense positions to the initial state without waiting for idle state."""
        self._transport.write(SystemHome().command())
        response = _strip_nl(self._transport.read())

        self._expect_ok(response)

    def home(self) -> None:
        """
        Reset internal state and lense positions to the initial state, waiting for the device to be idle.

        :param value: Desired magnification factor.
        :type value: float
        """
        with self._lock, self._wait_for_status_idle():
            self.home_unsafe()

    def _get_status_unsafe(self) -> str:
        self._transport.write(SystemStatus().query())
        response = _strip_nl(self._transport.read())

        return SystemStatus.parse_query_response(response)

    def get_status(self) -> str:
        """
        Get the current status of the device.

        :returns: Current system status string.
        :rtype: str
        """
        with self._lock:
            return self._get_status_unsafe()

    def get_error(self) -> str | BEXError:
        """
        Get the last error reported by the device.

        :returns: Error message or BEXError instance.
        :rtype: str or BEXError
        """
        with self._lock:
            self._transport.write(SystemErr().query())
            response = _strip_nl(self._transport.read())

        return SystemErr.parse_query_response(response)

    def get_version(self) -> str:
        """
        Get the firmware version string of the device.

        :returns: Device version information.
        :rtype: str
        """
        with self._lock:
            self._transport.write(SystemVersion().query())
            response = _strip_nl(self._transport.read())

        return SystemVersion.parse_query_response(response)

    def get_baudrate(self) -> str:
        """
        Get the baud rate.

        :returns: Baud rate.
        :rtype: str
        """
        with self._lock:
            self._transport.write(SystemBaudrate().query())
            response = _strip_nl(self._transport.read())

        return SystemBaudrate.parse_query_response(response)

    def set_baudrate(self, value: int) -> None:
        """
        Set the baud rate.

        :param value: Baudrate.
        :type value: int
        """
        with self._lock:
            self._transport.write(SystemBaudrate().command(value))
            response = _strip_nl(self._transport.read())

        self._expect_ok(response)

    def get_flags(self) -> SystemFlagsValue:
        """
        Get the system flags indicating current status.

        :returns: Parsed system flags.
        :rtype: SystemFlagsValue
        """
        with self._lock:
            self._transport.write(SystemFlags().query())
            response = _strip_nl(self._transport.read())

        return SystemFlags.parse_query_response(response)
