"""
OmniPreSense Radar Sensor Interface

A comprehensive, type-safe Python interface for OmniPreSense radar sensors.
Supports all OPS241/OPS242/OPS243 radar models with full API coverage. Based on
https://omnipresense.com/wp-content/uploads/2019/10/AN-010-Q_API_Interface.pdf

Features:
- Type-safe operations with comprehensive enums and data classes
- Support for Doppler (-A), FMCW (-B), and combined (-C) sensor types
- Complete API implementation with all commands
- Thread-safe serial communication
- Context manager support for automatic cleanup
- Comprehensive error handling and validation
- Rich documentation with examples

Example usage:
    ```python
    from new_radar import create_radar, Units, SamplingRate

    # Create radar sensor
    radar = create_radar('OPS243-A', '/dev/ttyACM0')

    # Use context manager for automatic cleanup
    with radar:
        radar.set_units(Units.METERS_PER_SECOND)
        radar.set_sampling_rate(SamplingRate.HZ_10000)

        def on_data(reading):
            print(f"Speed: {reading.speed} m/s, Direction: {reading.direction}")

        radar.start_streaming(on_data)
        time.sleep(10)
    ```

Author: Oskar Graeb graeb.oskar@gmail.com
License: MIT
"""

import json
import logging
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import Any, Callable, Dict, List, Optional, Type

import serial

# Configure logging
logger = logging.getLogger(__name__)


# =============================================================================
# Exceptions
# =============================================================================


class RadarError(Exception):
    """Base exception for all radar-related errors."""


class RadarConnectionError(RadarError):
    """Raised when connection to radar fails."""


class RadarCommandError(RadarError):
    """Raised when a radar command fails or returns an error."""


class RadarValidationError(RadarError):
    """Raised when parameter validation fails."""


class RadarTimeoutError(RadarError):
    """Raised when a radar operation times out."""


# =============================================================================
# Enums and Constants
# =============================================================================


class SensorType(Enum):
    """Radar sensor types with their capabilities."""

    DOPPLER_A = "OPS241-A"  # Motion, Speed, Direction
    DOPPLER_A2 = "OPS242-A"  # Enhanced Doppler
    DOPPLER_A3 = "OPS243-A"  # Advanced Doppler with range
    FMCW_B = "OPS241-B"  # Range only
    COMBINED_C = "OPS243-C"  # FMCW + Doppler


class Units(Enum):
    """Output units for speed and range measurements."""

    # Doppler units (speed)
    METERS_PER_SECOND = "m/s"
    KILOMETERS_PER_HOUR = "km/h"
    FEET_PER_SECOND = "ft/s"
    MILES_PER_HOUR = "mph"
    CENTIMETERS_PER_SECOND = "cm/s"

    # FMCW units (range)
    METERS = "m"
    CENTIMETERS = "cm"
    FEET = "ft"


class SamplingRate(IntEnum):
    """Available sampling rates in Hz."""

    HZ_1000 = 1000  # Max speed: 3.1 m/s, Resolution: 0.006 m/s
    HZ_5000 = 5000  # Max speed: 15.5 m/s, Resolution: 0.030 m/s
    HZ_10000 = 10000  # Max speed: 31.1 m/s, Resolution: 0.061 m/s
    HZ_20000 = 20000  # Max speed: 62.2 m/s, Resolution: 0.121 m/s
    HZ_50000 = 50000  # Max speed: 155.4 m/s, Resolution: 0.304 m/s
    HZ_100000 = 100000  # Max speed: 310.8 m/s, Resolution: 0.608 m/s


class Direction(Enum):
    """Object movement direction."""

    APPROACHING = "+"
    RECEDING = "-"
    UNKNOWN = "?"


class PowerMode(Enum):
    """Sensor power modes."""

    ACTIVE = "PA"  # Full power, continuous operation
    IDLE = "PI"  # Low power, periodic operation
    SLEEP = "PP"  # Minimal power, wake on command


class OutputMode(Enum):
    """Data output modes."""

    SPEED = "OS"  # Speed data only
    DIRECTION = "OD"  # Direction data
    JSON = "OJ"  # JSON formatted output
    MAGNITUDE = "OM"  # Signal magnitude
    RAW = "OR"  # Raw ADC data
    FFT = "OF"  # Post-FFT data
    TIMESTAMP = "OT"  # Include timestamps
    UNITS = "OU"  # Include units in output


# =============================================================================
# Data Structures
# =============================================================================


@dataclass
class RadarReading:
    """Represents a single radar measurement."""

    timestamp: float = field(default_factory=time.time)
    speed: Optional[float] = None
    direction: Optional[Direction] = None
    range_m: Optional[float] = None
    magnitude: Optional[float] = None
    raw_data: Optional[str] = None

    def __str__(self) -> str:
        parts = [f"t={self.timestamp:.3f}"]
        if self.speed is not None:
            parts.append(f"speed={self.speed}")
        if self.direction:
            parts.append(f"dir={self.direction.value}")
        if self.range_m is not None:
            parts.append(f"range={self.range_m}m")
        if self.magnitude is not None:
            parts.append(f"mag={self.magnitude}")
        return f"RadarReading({', '.join(parts)})"


@dataclass
class SensorInfo:
    """Radar sensor information and capabilities."""

    model: str
    firmware_version: str
    board_id: str
    frequency: float
    has_doppler: bool
    has_fmcw: bool
    max_range: float
    detection_range: str


@dataclass
class RadarConfig:
    """Complete radar sensor configuration."""

    units: Units = Units.METERS_PER_SECOND
    sampling_rate: SamplingRate = SamplingRate.HZ_10000
    data_precision: int = 2
    magnitude_threshold: int = 20
    speed_filter_min: Optional[float] = None
    speed_filter_max: Optional[float] = None
    range_filter_min: Optional[float] = None
    range_filter_max: Optional[float] = None
    direction_filter: Optional[Direction] = None
    power_mode: PowerMode = PowerMode.ACTIVE
    output_modes: List[OutputMode] = field(default_factory=lambda: [OutputMode.SPEED])
    buffer_size: int = 1024
    duty_cycle_short: int = 0
    duty_cycle_long: int = 0


# =============================================================================
# Base Radar Sensor Class
# =============================================================================


class OPSRadarSensor(ABC):
    """
    Abstract base class for OmniPreSense radar sensors.

    Provides common functionality for serial communication, command handling,
    and data processing that's shared across all sensor types.
    """

    # Command mappings
    SAMPLING_RATE_COMMANDS = {
        SamplingRate.HZ_1000: "SI",
        SamplingRate.HZ_5000: "SV",
        SamplingRate.HZ_10000: "SX",
        SamplingRate.HZ_20000: "S2",
        SamplingRate.HZ_50000: "SL",
        SamplingRate.HZ_100000: "SC",
    }

    POWER_MODE_COMMANDS = {
        PowerMode.ACTIVE: "PA",
        PowerMode.IDLE: "PI",
        PowerMode.SLEEP: "PP",
    }

    # Duty cycle command mappings
    DUTY_CYCLE_COMMANDS = {
        0: "W0",
        1: "WI",
        5: "WV",
        10: "WX",
        20: "W2",
        50: "WL",
        100: "WC",
        200: "W2",
        300: "W3",
        400: "W4",
        500: "WD",
        600: "WM",
        700: "W7",
        800: "W8",
        900: "W9",
        1000: "WT",
    }

    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 0.1):
        """
        Initialize radar sensor.

        Args:
            port: Serial port name (e.g., '/dev/ttyUSB0', 'COM3')
            baudrate: Serial communication speed (default: 115200)
            timeout: Serial read timeout in seconds (default: 1.0)
        """
        self.port_name = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser: Optional[serial.Serial] = None
        self._reader_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._callback: Optional[Callable[[RadarReading], None]] = None
        self._config = RadarConfig()
        self._sensor_info: Optional[SensorInfo] = None
        self._lock = threading.RLock()

        logger.info(f"Initialized {self.__class__.__name__} on port {port}")

    # Context manager support
    def __enter__(self) -> "OPSRadarSensor":
        """Context manager entry - opens connection."""
        if not self.open():
            raise RadarConnectionError(f"Failed to open connection to {self.port_name}")
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit - closes connection."""
        self.close()

    def open(self) -> bool:
        """
        Open serial connection to radar sensor.

        Returns:
            bool: True if connection successful, False otherwise

        Raises:
            RadarConnectionError: If connection fails
        """
        try:
            self.ser = serial.Serial(
                port=self.port_name,
                baudrate=self.baudrate,
                timeout=self.timeout,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
            )
            logger.info(f"Opened radar serial connection: {self.port_name}")

            # Get sensor info on connection
            self._sensor_info = self._get_sensor_info()
            return True

        except Exception as e:
            logger.error(f"Failed to open radar serial connection: {e}")
            self.ser = None
            raise RadarConnectionError(f"Failed to connect to radar: {e}") from e

    def close(self) -> None:
        """Close serial connection and stop reader thread."""
        self.stop_streaming()

        if self.ser and self.ser.is_open:
            try:
                self.ser.close()
                logger.info("Closed radar serial connection")
            except Exception as e:
                logger.error(f"Error closing radar serial connection: {e}")
        self.ser = None

    def is_connected(self) -> bool:
        """Check if radar sensor is connected."""
        return self.ser is not None and self.ser.is_open

    def send_command(
        self, command: str, expect_response: bool = False, timeout: float = 1.0
    ) -> Optional[str]:
        """
        Send command to radar sensor.

        Args:
            command: Command string to send
            expect_response: Whether to wait for and return response
            timeout: Response timeout in seconds

        Returns:
            Optional[str]: Response if expect_response=True, None otherwise

        Raises:
            RadarCommandError: If command fails or times out
        """
        if not self.is_connected():
            raise RadarCommandError("Radar not connected")

        with self._lock:
            try:
                # Add newline if not present
                if not command.endswith("\n"):
                    command += "\n"

                if self.ser is not None:
                    self.ser.write(command.encode("ascii"))
                    self.ser.flush()
                else:
                    raise RadarCommandError("Serial connection not available")
                logger.debug(f"Sent radar command: {command.strip()}")

                if expect_response:
                    # Wait for response
                    if self.ser is not None:
                        response = (
                            self.ser.readline().decode("ascii", errors="ignore").strip()
                        )
                    else:
                        raise RadarCommandError("Serial connection not available")
                    if response:
                        logger.debug(f"Received response: {response}")
                        return response
                    else:
                        raise RadarTimeoutError(
                            f"No response to command: {command.strip()}"
                        )

                time.sleep(0.05)  # Small delay for command processing
                return None

            except serial.SerialException as e:
                logger.error(f"Serial error sending command '{command.strip()}': {e}")
                raise RadarCommandError(f"Serial communication error: {e}") from e
            except Exception as e:
                logger.error(f"Error sending command '{command.strip()}': {e}")
                raise RadarCommandError(f"Command failed: {e}") from e

    # =============================================================================
    # Module Information Commands
    # =============================================================================

    def get_sensor_info(self) -> SensorInfo:
        """Get comprehensive sensor information."""
        if self._sensor_info is None:
            self._sensor_info = self._get_sensor_info()
        return self._sensor_info

    def _get_sensor_info(self) -> SensorInfo:
        """Internal method to query sensor information."""
        try:
            # Get basic info
            response = self.send_command("??", expect_response=True) or "Unknown"

            # Parse the JSON response if available
            version = "Unknown"
            board_id = "Unknown"
            freq_val = 0.0

            if response and response != "Unknown":
                try:
                    # Handle multiple JSON objects in response
                    lines = response.strip().split("\n")
                    for line in lines:
                        if line.strip().startswith("{"):
                            data = json.loads(line.strip())
                            if "Version" in data:
                                version = data["Version"]
                            elif "rev" in data:
                                board_id = data["rev"]
                            elif "Product" in data and "OPS243-C" in data["Product"]:
                                freq_val = 24.125e9  # 24.125 GHz for OPS243-C
                except (json.JSONDecodeError, ValueError) as e:
                    logger.debug(f"JSON parsing error: {e}")
                    # Fallback to simple parsing
                    version = response[:50] if len(response) > 50 else response

            # Try to get board ID separately if not found
            if board_id == "Unknown":
                board_id = self.send_command("?P", expect_response=True) or "Unknown"

            # Try to get frequency separately if not found
            if freq_val == 0.0:
                frequency = self.send_command("?F", expect_response=True) or "0"
                try:
                    freq_val = float(frequency.split()[-1]) if frequency != "0" else 0.0
                except (ValueError, IndexError):
                    freq_val = 0.0

            # Determine sensor capabilities based on model
            model = self.__class__.__name__
            has_doppler = "Doppler" in model or "Combined" in model
            has_fmcw = "FMCW" in model or "Combined" in model

            # For OPS243C, it has both capabilities
            if "OPS243C" in model:
                has_doppler = True
                has_fmcw = True

            # Set detection ranges based on sensor type
            if "OPS241" in model:
                max_range = 25.0
                detection_range = "20-25m"
            elif "OPS242" in model:
                max_range = 25.0
                detection_range = "20-25m"
            elif "OPS243" in model and has_doppler and not has_fmcw:
                max_range = 100.0
                detection_range = "75-100m"
            elif "OPS241" in model and has_fmcw:
                max_range = 20.0
                detection_range = "15-20m"
            elif "OPS243" in model and has_fmcw:
                max_range = 60.0
                detection_range = "50-60m"
            else:
                max_range = 25.0
                detection_range = "Unknown"

            return SensorInfo(
                model=model,
                firmware_version=version,
                board_id=board_id,
                frequency=freq_val,
                has_doppler=has_doppler,
                has_fmcw=has_fmcw,
                max_range=max_range,
                detection_range=detection_range,
            )

        except Exception as e:
            logger.warning(f"Could not get complete sensor info: {e}")
            return SensorInfo(
                model=self.__class__.__name__,
                firmware_version="Unknown",
                board_id="Unknown",
                frequency=0.0,
                has_doppler="Doppler" in self.__class__.__name__,
                has_fmcw="FMCW" in self.__class__.__name__,
                max_range=25.0,
                detection_range="Unknown",
            )

    def get_firmware_version(self) -> str:
        """Get firmware version string."""
        return self.send_command("??", expect_response=True) or "Unknown"

    def get_board_id(self) -> str:
        """Get board ID."""
        return self.send_command("?P", expect_response=True) or "Unknown"

    def get_frequency(self) -> float:
        """Get operating frequency in Hz."""
        response = self.send_command("?F", expect_response=True)
        try:
            return float(response.split()[-1]) if response else 0.0
        except (ValueError, IndexError):
            return 0.0

    # =============================================================================
    # Configuration Commands
    # =============================================================================

    def set_units(self, units: Units) -> None:
        """
        Set output units for measurements.

        Args:
            units: Units enum value for speed or range

        Raises:
            RadarValidationError: If units not supported by sensor type
        """
        self._validate_units(units)

        # Map units to commands - different for Doppler vs FMCW
        doppler_commands = {
            Units.METERS_PER_SECOND: "UM",
            Units.KILOMETERS_PER_HOUR: "UK",
            Units.FEET_PER_SECOND: "UF",
            Units.MILES_PER_HOUR: "US",
            Units.CENTIMETERS_PER_SECOND: "UC",
        }

        fmcw_commands = {Units.METERS: "uM", Units.CENTIMETERS: "uC", Units.FEET: "uF"}

        if units in doppler_commands and self.get_sensor_info().has_doppler:
            self.send_command(doppler_commands[units])
        elif units in fmcw_commands and self.get_sensor_info().has_fmcw:
            self.send_command(fmcw_commands[units])
        else:
            raise RadarValidationError(f"Units {units} not supported by this sensor")

        self._config.units = units
        logger.info(f"Set units to {units.value}")

    def set_sampling_rate(self, rate: SamplingRate) -> None:
        """
        Set sampling rate.

        Args:
            rate: SamplingRate enum value
        """
        if not self.get_sensor_info().has_doppler:
            raise RadarValidationError("Sampling rate only applies to Doppler sensors")

        command = self.SAMPLING_RATE_COMMANDS[rate]
        self.send_command(command)
        self._config.sampling_rate = rate
        logger.info(f"Set sampling rate to {rate.value} Hz")

    def set_data_precision(self, precision: int) -> None:
        """
        Set data precision (decimal places).

        Args:
            precision: Number of decimal places (0-9)
        """
        if not 0 <= precision <= 9:
            raise RadarValidationError("Precision must be 0-9")

        self.send_command(f"F{precision}")
        self._config.data_precision = precision
        logger.info(f"Set data precision to {precision} decimal places")

    def set_magnitude_threshold(self, threshold: int, doppler: bool = True) -> None:
        """
        Set magnitude threshold for detection.

        Args:
            threshold: Magnitude threshold value
            doppler: True for Doppler threshold, False for FMCW
        """
        if threshold < 0:
            raise RadarValidationError("Threshold must be non-negative")

        if doppler:
            self.send_command(f"M>{threshold}")
        else:
            self.send_command(f"m>{threshold}")

        self._config.magnitude_threshold = threshold
        logger.info(f"Set magnitude threshold to {threshold}")

    def set_power_mode(self, mode: PowerMode) -> None:
        """
        Set sensor power mode.

        Args:
            mode: PowerMode enum value
        """
        command = self.POWER_MODE_COMMANDS[mode]
        self.send_command(command)
        self._config.power_mode = mode
        logger.info(f"Set power mode to {mode.value}")

    def set_buffer_size(self, size: int) -> None:
        """
        Set sampling buffer size.

        Args:
            size: Buffer size (valid values depend on sensor)
        """
        if size <= 0:
            raise RadarValidationError("Buffer size must be positive")

        # Map common sizes to commands
        size_commands = {
            64: "S<",
            128: "S{",
            256: "S}",
            512: "S>",
            1024: "S>",
            2048: "S]",
        }

        # Find closest valid size
        valid_sizes = list(size_commands.keys())
        closest_size = min(valid_sizes, key=lambda x: abs(x - size))

        if abs(closest_size - size) > size * 0.1:  # 10% tolerance
            logger.warning(f"Requested size {size} not available, using {closest_size}")

        self.send_command(size_commands[closest_size])
        self._config.buffer_size = closest_size
        logger.info(f"Set buffer size to {closest_size}")

    def set_duty_cycle(self, short_ms: int, long_ms: int = 0) -> None:
        """
        Set duty cycle timing.

        Args:
            short_ms: Short duty cycle delay in milliseconds
            long_ms: Long duty cycle delay in milliseconds (optional)
        """
        # Find closest valid short duty cycle value
        valid_values = list(self.DUTY_CYCLE_COMMANDS.keys())
        closest_short = min(valid_values, key=lambda x: abs(x - short_ms))

        if closest_short in self.DUTY_CYCLE_COMMANDS:
            self.send_command(self.DUTY_CYCLE_COMMANDS[closest_short])
            self._config.duty_cycle_short = closest_short
            logger.info(f"Set short duty cycle to {closest_short}ms")

        if long_ms > 0:
            # Long duty cycle uses different command format
            self.send_command(f"Z={long_ms}")
            self._config.duty_cycle_long = long_ms
            logger.info(f"Set long duty cycle to {long_ms}ms")

    # =============================================================================
    # Filter Commands
    # =============================================================================

    def set_speed_filter(
        self, min_speed: Optional[float] = None, max_speed: Optional[float] = None
    ) -> None:
        """
        Set speed filtering range.

        Args:
            min_speed: Minimum speed threshold (None to disable)
            max_speed: Maximum speed threshold (None to disable)
        """
        if not self.get_sensor_info().has_doppler:
            raise RadarValidationError(
                "Speed filtering only applies to Doppler sensors"
            )

        if min_speed is not None:
            if min_speed < 0:
                raise RadarValidationError("Minimum speed must be non-negative")
            self.send_command(f"R>{min_speed}")
            self._config.speed_filter_min = min_speed
            logger.info(f"Set minimum speed filter to {min_speed}")

        if max_speed is not None:
            if max_speed < 0:
                raise RadarValidationError("Maximum speed must be non-negative")
            if min_speed is not None and max_speed <= min_speed:
                raise RadarValidationError("Maximum speed must be greater than minimum")
            self.send_command(f"R<{max_speed}")
            self._config.speed_filter_max = max_speed
            logger.info(f"Set maximum speed filter to {max_speed}")

    def set_range_filter(
        self, min_range: Optional[float] = None, max_range: Optional[float] = None
    ) -> None:
        """
        Set range filtering range.

        Args:
            min_range: Minimum range threshold (None to disable)
            max_range: Maximum range threshold (None to disable)
        """
        if not self.get_sensor_info().has_fmcw:
            raise RadarValidationError("Range filtering only applies to FMCW sensors")

        if min_range is not None:
            if min_range < 0:
                raise RadarValidationError("Minimum range must be non-negative")
            self.send_command(f"r>{min_range}")
            self._config.range_filter_min = min_range
            logger.info(f"Set minimum range filter to {min_range}")

        if max_range is not None:
            if max_range < 0:
                raise RadarValidationError("Maximum range must be non-negative")
            if min_range is not None and max_range <= min_range:
                raise RadarValidationError("Maximum range must be greater than minimum")
            self.send_command(f"r<{max_range}")
            self._config.range_filter_max = max_range
            logger.info(f"Set maximum range filter to {max_range}")

    def set_direction_filter(self, direction: Optional[Direction] = None) -> None:
        """
        Set direction filtering.

        Args:
            direction: Direction to filter for (None to disable)
        """
        if not self.get_sensor_info().has_doppler:
            raise RadarValidationError(
                "Direction filtering only applies to Doppler sensors"
            )

        if direction == Direction.APPROACHING:
            self.send_command("R+")
        elif direction == Direction.RECEDING:
            self.send_command("R-")
        elif direction is None:
            self.send_command("R|")  # Clear direction filter
        else:
            raise RadarValidationError(f"Invalid direction: {direction}")

        self._config.direction_filter = direction
        logger.info(f"Set direction filter to {direction}")

    # =============================================================================
    # Output Control Commands
    # =============================================================================

    def enable_output_mode(self, mode: OutputMode, enable: bool = True) -> None:
        """
        Enable or disable specific output mode.

        Args:
            mode: OutputMode enum value
            enable: True to enable, False to disable
        """
        # Most output modes are toggles - send command to enable
        if enable:
            self.send_command(mode.value)
            if mode not in self._config.output_modes:
                self._config.output_modes.append(mode)
        else:
            # Some modes have explicit disable commands
            disable_commands = {
                OutputMode.JSON: "O/",
                OutputMode.MAGNITUDE: "OM",  # Toggle
                OutputMode.TIMESTAMP: "OT",  # Toggle
            }
            if mode in disable_commands:
                self.send_command(disable_commands[mode])

            if mode in self._config.output_modes:
                self._config.output_modes.remove(mode)

        logger.info(f"{'Enabled' if enable else 'Disabled'} output mode: {mode.value}")

    def enable_json_output(self, enable: bool = True) -> None:
        """Enable/disable JSON formatted output."""
        self.enable_output_mode(OutputMode.JSON, enable)

    def enable_magnitude_output(self, enable: bool = True) -> None:
        """Enable/disable signal magnitude in output."""
        self.enable_output_mode(OutputMode.MAGNITUDE, enable)

    def enable_timestamp_output(self, enable: bool = True) -> None:
        """Enable/disable timestamps in output."""
        self.enable_output_mode(OutputMode.TIMESTAMP, enable)

    # =============================================================================
    # Data Streaming
    # =============================================================================

    def start_streaming(self, callback: Callable[[RadarReading], None]) -> None:
        """
        Start streaming radar data with callback.

        Args:
            callback: Function called for each radar reading
        """
        if self._reader_thread and self._reader_thread.is_alive():
            logger.warning("Data streaming already active")
            return

        self._callback = callback
        self._stop_event.clear()
        self._reader_thread = threading.Thread(target=self._read_loop, daemon=True)
        self._reader_thread.start()
        logger.info("Started radar data streaming")

    def stop_streaming(self) -> None:
        """Stop radar data streaming."""
        if self._reader_thread and self._reader_thread.is_alive():
            logger.info("Stopping radar data streaming...")
            self._stop_event.set()
            self._reader_thread.join(timeout=2.0)
            if self._reader_thread.is_alive():
                logger.warning("Data streaming thread did not stop cleanly")
            else:
                logger.info("Radar data streaming stopped")
        self._reader_thread = None
        self._callback = None

    def _read_loop(self) -> None:
        """Main data reading loop - runs in separate thread."""
        logger.debug("Radar data reader thread started")
        buf = b""

        while not self._stop_event.is_set():
            try:
                if not self.is_connected():
                    break

                # Read chunk with timeout
                chunk = self.ser.read(1024) if self.ser else b""
                if not chunk:
                    continue

                buf += chunk

                # Process complete lines from buffer
                while b"\n" in buf:
                    line, buf = buf.split(b"\n", 1)
                    try:
                        line_str = line.decode("ascii", errors="ignore").strip()
                    except Exception as e:
                        logger.debug(f"Error decoding line: {e}")
                        line_str = ""

                    if line_str and self._callback:
                        try:
                            reading = self._parse_radar_data(line_str)
                            if reading:
                                self._callback(reading)
                        except Exception as e:
                            logger.debug(f"Error in callback: {e}")

            except serial.SerialTimeoutException:
                continue  # Normal timeout, continue loop
            except Exception as e:
                if not self._stop_event.is_set():
                    logger.error(f"Radar read error: {e}")
                break

        # Process any remaining data in buffer
        if buf and self._callback:
            try:
                remaining_str = buf.decode("ascii", errors="ignore").strip()
                if remaining_str:
                    reading = self._parse_radar_data(remaining_str)
                    if reading:
                        self._callback(reading)
            except Exception as e:
                logger.debug(f"Error parsing radar data: {e}")

        logger.debug("Radar data reader thread ended")

    @abstractmethod
    def _parse_radar_data(self, data: str) -> Optional[RadarReading]:
        """
        Parse raw radar data string into RadarReading object.
        Must be implemented by sensor-specific subclasses.

        Args:
            data: Raw data string from radar

        Returns:
            RadarReading object or None if data cannot be parsed
        """

    @abstractmethod
    def _validate_units(self, units: Units) -> None:
        """
        Validate that units are supported by this sensor type.
        Must be implemented by sensor-specific subclasses.

        Args:
            units: Units enum value to validate

        Raises:
            RadarValidationError: If units not supported
        """

    # =============================================================================
    # Utility Methods
    # =============================================================================

    def get_config(self) -> RadarConfig:
        """Get current radar configuration."""
        return self._config

    def reset_sensor(self) -> None:
        """Reset sensor to default settings."""
        self.send_command("A!")
        self._config = RadarConfig()  # Reset local config
        logger.info("Sensor reset to defaults")

    def save_config_to_memory(self) -> None:
        """Save current configuration to persistent memory."""
        self.send_command("A.")
        logger.info("Configuration saved to persistent memory")

    def __str__(self) -> str:
        """String representation of radar sensor."""
        info = self.get_sensor_info()
        return f"{info.model} on {self.port_name} (FW: {info.firmware_version})"

    def __repr__(self) -> str:
        """Detailed string representation."""
        return (
            f"{self.__class__.__name__}(port='{self.port_name}', "
            f"baudrate={self.baudrate}, connected={self.is_connected()})"
        )


# =============================================================================
# Specialized Sensor Classes
# =============================================================================


class OPS241A_DopplerRadar(OPSRadarSensor):
    """
    OPS241-A Doppler radar sensor.

    Features:
    - Motion detection
    - Speed measurement
    - Direction detection
    - Signal magnitude
    - Detection range: 20-25m (RCS = 10)
    """

    def _validate_units(self, units: Units) -> None:
        """Validate units for Doppler sensor."""
        doppler_units = {
            Units.METERS_PER_SECOND,
            Units.KILOMETERS_PER_HOUR,
            Units.FEET_PER_SECOND,
            Units.MILES_PER_HOUR,
            Units.CENTIMETERS_PER_SECOND,
        }
        if units not in doppler_units:
            raise RadarValidationError(
                f"OPS241-A only supports speed units: {[u.value for u in doppler_units]}"
            )

    def _parse_radar_data(self, data: str) -> Optional[RadarReading]:
        """Parse OPS241-A Doppler radar data."""
        try:
            # Handle JSON output
            if data.startswith("{"):
                return self._parse_json_data(data)

            # Handle standard output format: "speed direction magnitude" or "speed direction"
            parts = data.split()
            if len(parts) >= 2:
                speed = float(parts[0])
                direction = (
                    Direction.APPROACHING if parts[1] == "+" else Direction.RECEDING
                )
                magnitude = float(parts[2]) if len(parts) > 2 else None

                return RadarReading(
                    speed=abs(speed),  # Speed is always positive
                    direction=direction,
                    magnitude=magnitude,
                    raw_data=data.strip(),
                )

        except (ValueError, IndexError) as e:
            logger.debug(f"Could not parse radar data '{data}': {e}")

        return None

    def _parse_json_data(self, data: str) -> Optional[RadarReading]:
        """Parse JSON formatted radar data."""
        try:
            json_data = json.loads(data)
            return RadarReading(
                speed=abs(float(json_data.get("speed", 0))),
                direction=(
                    Direction.APPROACHING
                    if json_data.get("direction") == "+"
                    else Direction.RECEDING
                ),
                magnitude=(
                    float(json_data.get("magnitude", 0))
                    if "magnitude" in json_data
                    else None
                ),
                timestamp=float(json_data.get("time", time.time())),
            )
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.debug(f"Could not parse JSON data '{data}': {e}")
            return None


class OPS242A_DopplerRadar(OPS241A_DopplerRadar):
    """
    OPS242-A Enhanced Doppler radar sensor.

    Features:
    - All OPS241-A features
    - Enhanced sensitivity and range
    - Detection range: 20-25m (RCS = 10)
    """


class OPS243A_DopplerRadar(OPS241A_DopplerRadar):
    """
    OPS243-A Advanced Doppler radar sensor.

    Features:
    - All OPS241-A features
    - Range measurement (pending in firmware)
    - FCC/IC modular approval
    - Detection range: 75-100m (RCS = 10)
    """


class OPS241B_FMCWRadar(OPSRadarSensor):
    """
    OPS241-B FMCW radar sensor.

    Features:
    - Range measurement only
    - Signal magnitude
    - Detection range: 15-20m (RCS = 10)
    """

    def _validate_units(self, units: Units) -> None:
        """Validate units for FMCW sensor."""
        fmcw_units = {Units.METERS, Units.CENTIMETERS, Units.FEET}
        if units not in fmcw_units:
            raise RadarValidationError(
                f"OPS241-B only supports range units: {[u.value for u in fmcw_units]}"
            )

    def _parse_radar_data(self, data: str) -> Optional[RadarReading]:
        """Parse OPS241-B FMCW radar data."""
        try:
            # Handle JSON output
            if data.startswith("{"):
                return self._parse_json_data(data)

            # Handle standard output format: "range magnitude" or "range"
            parts = data.split()
            if len(parts) >= 1:
                range_m = float(parts[0])
                magnitude = float(parts[1]) if len(parts) > 1 else None

                return RadarReading(range_m=range_m, magnitude=magnitude)

        except (ValueError, IndexError) as e:
            logger.debug(f"Could not parse radar data '{data}': {e}")

        return None

    def _parse_json_data(self, data: str) -> Optional[RadarReading]:
        """Parse JSON formatted radar data."""
        try:
            json_data = json.loads(data)
            return RadarReading(
                range_m=float(json_data.get("range", 0)),
                magnitude=(
                    float(json_data.get("magnitude", 0))
                    if "magnitude" in json_data
                    else None
                ),
                timestamp=float(json_data.get("time", time.time())),
            )
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.debug(f"Could not parse JSON data '{data}': {e}")
            return None


class OPS243C_CombinedRadar(OPSRadarSensor):
    """
    OPS243-C Combined FMCW & Doppler radar sensor.

    Features:
    - Motion detection
    - Speed measurement
    - Direction detection
    - Range measurement
    - Signal magnitude
    - FCC/IC modular approval
    - Detection range: 50-60m (RCS = 10)
    """

    def _validate_units(self, units: Units) -> None:
        """Validate units for combined sensor - supports both speed and range units."""
        # Combined sensor supports all units
        all_units = set(Units)
        if units not in all_units:
            raise RadarValidationError(f"Invalid units: {units}")

    def _parse_radar_data(self, data: str) -> Optional[RadarReading]:
        """Parse OPS243-C combined radar data."""
        try:
            # Handle JSON output
            if data.startswith("{"):
                return self._parse_json_data(data)

            # Handle OPS243-C specific format: "units",value or "units",value,extra
            # Example: "m",2.1 or "kmph",48,-1.3
            if '"' in data and "," in data:
                # Parse format like "m",2.1 or "kmph",48,-1.3
                parts = data.split(",")
                if len(parts) >= 2:
                    units_part = parts[0].strip().strip('"')
                    value_str = parts[1].strip()

                    try:
                        value = float(value_str)
                        reading = RadarReading(raw_data=data.strip())

                        # Determine if this is speed or range based on units
                        if units_part in ["mps", "mph", "kmh", "kmph", "m/s", "km/h"]:
                            # Speed data
                            reading.speed = abs(value)
                            # OPS243-C typically sends positive for approaching, negative for receding
                            reading.direction = (
                                Direction.APPROACHING
                                if value >= 0
                                else Direction.RECEDING
                            )
                            
                            # Check for third value (might be additional data or range)
                            if len(parts) >= 3:
                                try:
                                    third_val = float(parts[2].strip())
                                    # If it's a reasonable range value, use it
                                    if 0 < abs(third_val) < 100:  # Reasonable range in meters
                                        reading.range_m = abs(third_val)
                                except ValueError:
                                    pass
                                    
                        elif units_part in ["m", "ft", "cm"]:
                            # Range data
                            reading.range_m = value

                        return reading
                    except ValueError:
                        pass

            # Handle standard output format: "speed direction range magnitude"
            # or various combinations depending on enabled outputs
            parts = data.split()
            if len(parts) >= 1:
                reading = RadarReading(raw_data=data.strip())

                # Parse based on number of parts and content
                if len(parts) >= 4:
                    # Full format: speed, direction, range, magnitude
                    reading.speed = abs(float(parts[0]))
                    reading.direction = (
                        Direction.APPROACHING if parts[1] == "+" else Direction.RECEDING
                    )
                    reading.range_m = float(parts[2])
                    reading.magnitude = float(parts[3])
                elif len(parts) == 3:
                    # Could be speed+direction+range or speed+direction+magnitude
                    reading.speed = abs(float(parts[0]))
                    reading.direction = (
                        Direction.APPROACHING if parts[1] == "+" else Direction.RECEDING
                    )
                    # Heuristic: if third value is large, it's probably magnitude
                    third_val = float(parts[2])
                    if third_val > 100:  # Typical magnitude values are > 100
                        reading.magnitude = third_val
                    else:
                        reading.range_m = third_val
                elif len(parts) == 2:
                    # Could be speed+direction or range+magnitude
                    first_val = float(parts[0])
                    if parts[1] in ["+", "-"]:
                        # Speed and direction
                        reading.speed = abs(first_val)
                        reading.direction = (
                            Direction.APPROACHING
                            if parts[1] == "+"
                            else Direction.RECEDING
                        )
                    else:
                        # Range and magnitude
                        reading.range_m = first_val
                        reading.magnitude = float(parts[1])
                else:
                    # Single value - could be speed or range
                    val = float(parts[0])
                    # Heuristic: speeds are typically < 50, ranges can be higher
                    if val < 50:
                        reading.speed = abs(val)
                    else:
                        reading.range_m = val

                return reading

        except (ValueError, IndexError) as e:
            logger.debug(f"Could not parse radar data '{data}': {e}")

        return None

    def _parse_json_data(self, data: str) -> Optional[RadarReading]:
        """Parse JSON formatted radar data."""
        try:
            json_data = json.loads(data)
            return RadarReading(
                speed=(
                    abs(float(json_data.get("speed", 0)))
                    if "speed" in json_data
                    else None
                ),
                direction=(
                    Direction.APPROACHING
                    if json_data.get("direction") == "+"
                    else (
                        Direction.RECEDING
                        if json_data.get("direction") == "-"
                        else None
                    )
                ),
                range_m=(
                    float(json_data.get("range", 0)) if "range" in json_data else None
                ),
                magnitude=(
                    float(json_data.get("magnitude", 0))
                    if "magnitude" in json_data
                    else None
                ),
                timestamp=float(json_data.get("time", time.time())),
            )
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.debug(f"Could not parse JSON data '{data}': {e}")
            return None


# =============================================================================
# Factory Functions and Utilities
# =============================================================================


def create_radar(model: str, port: str, **kwargs: Any) -> OPSRadarSensor:
    """
    Factory function to create appropriate radar sensor instance.

    Args:
        model: Radar model string (e.g., 'OPS241-A', 'OPS243-C')
        port: Serial port name
        **kwargs: Additional arguments passed to sensor constructor

    Returns:
        Appropriate radar sensor instance

    Raises:
        RadarValidationError: If model is not supported

    Example:
        ```python
        radar = create_radar('OPS243-A', '/dev/ttyUSB0')
        with radar:
            radar.set_units(Units.METERS_PER_SECOND)
            # ... use radar
        ```
    """
    model = model.upper().replace("-", "").replace("_", "")

    sensor_classes: Dict[str, Type[OPSRadarSensor]] = {
        "OPS241A": OPS241A_DopplerRadar,
        "OPS242A": OPS242A_DopplerRadar,
        "OPS243A": OPS243A_DopplerRadar,
        "OPS241B": OPS241B_FMCWRadar,
        "OPS243C": OPS243C_CombinedRadar,
    }

    if model not in sensor_classes:
        available = ", ".join(sensor_classes.keys())
        raise RadarValidationError(
            f"Unsupported radar model '{model}'. Available: {available}"
        )

    sensor_class = sensor_classes[model]
    return sensor_class(port, **kwargs)


def get_supported_models() -> List[str]:
    """
    Get list of supported radar models.

    Returns:
        List of supported model strings
    """
    return ["OPS241-A", "OPS242-A", "OPS243-A", "OPS241-B", "OPS243-C"]


def get_model_info(model: str) -> Dict[str, Any]:
    """
    Get information about a specific radar model.

    Args:
        model: Radar model string

    Returns:
        Dictionary with model information

    Example:
        ```python
        info = get_model_info('OPS243-C')
        print(f"Detection range: {info['detection_range']}")
        ```
    """
    model_info = {
        "OPS241-A": {
            "type": "Doppler",
            "features": ["Motion", "Speed", "Direction", "Signal Magnitude"],
            "detection_range": "20-25m",
            "max_speed": "31.1 m/s @ 10kHz",
            "fcc_approved": False,
        },
        "OPS242-A": {
            "type": "Doppler",
            "features": ["Motion", "Speed", "Direction", "Signal Magnitude"],
            "detection_range": "20-25m",
            "max_speed": "31.1 m/s @ 10kHz",
            "fcc_approved": False,
        },
        "OPS243-A": {
            "type": "Doppler",
            "features": [
                "Motion",
                "Speed",
                "Direction",
                "Signal Magnitude",
                "Range (pending)",
            ],
            "detection_range": "75-100m",
            "max_speed": "31.1 m/s @ 10kHz",
            "fcc_approved": True,
        },
        "OPS241-B": {
            "type": "FMCW",
            "features": ["Range", "Signal Magnitude"],
            "detection_range": "15-20m",
            "max_speed": "N/A",
            "fcc_approved": False,
        },
        "OPS243-C": {
            "type": "FMCW & Doppler",
            "features": ["Motion", "Speed", "Direction", "Range", "Signal Magnitude"],
            "detection_range": "50-60m",
            "max_speed": "31.1 m/s @ 10kHz",
            "fcc_approved": True,
        },
    }

    model = model.upper()
    if model not in model_info:
        raise RadarValidationError(f"Unknown model: {model}")

    return model_info[model]


# =============================================================================
# Usage Examples and Demonstrations
# =============================================================================


def example_doppler_usage() -> None:
    """Example usage of Doppler radar sensor."""
    print("=== Doppler Radar Example ===")

    # Create radar sensor
    radar = create_radar("OPS243-A", "/dev/ttyUSB0")

    try:
        with radar:
            # Configure sensor
            radar.set_units(Units.METERS_PER_SECOND)
            radar.set_sampling_rate(SamplingRate.HZ_10000)
            radar.set_magnitude_threshold(20)
            radar.set_speed_filter(min_speed=0.5, max_speed=25.0)

            # Enable JSON output for easier parsing
            radar.enable_json_output(True)
            radar.enable_magnitude_output(True)

            # Data callback
            def on_detection(reading: RadarReading) -> None:
                if reading.speed and reading.speed > 1.0:  # Filter slow movements
                    print(
                        f"Detected: {reading.speed:.2f} m/s "
                        f"({reading.direction.value if reading.direction else '?'}) "
                        f"Magnitude: {reading.magnitude:.0f}"
                    )

            # Start streaming
            print("Starting radar detection...")
            radar.start_streaming(on_detection)

            # Run for 30 seconds
            time.sleep(30)

    except RadarError as e:
        print(f"Radar error: {e}")
    except KeyboardInterrupt:
        print("Stopped by user")


def example_fmcw_usage() -> None:
    """Example usage of FMCW radar sensor."""
    print("=== FMCW Radar Example ===")

    radar = create_radar("OPS241-B", "/dev/ttyUSB0")

    try:
        with radar:
            # Configure for range measurement
            radar.set_units(Units.METERS)
            radar.set_magnitude_threshold(150)
            radar.set_range_filter(min_range=0.5, max_range=15.0)

            def on_range_detection(reading: RadarReading) -> None:
                if reading.range_m:
                    print(
                        f"Range: {reading.range_m:.2f} m, "
                        f"Magnitude: {reading.magnitude:.0f}"
                    )

            print("Starting range detection...")
            radar.start_streaming(on_range_detection)
            time.sleep(30)

    except RadarError as e:
        print(f"Radar error: {e}")


def example_combined_usage() -> None:
    """Example usage of combined FMCW + Doppler radar."""
    print("=== Combined Radar Example ===")

    radar = create_radar("OPS243-C", "/dev/ttyUSB0")

    try:
        with radar:
            # Configure for both speed and range
            radar.set_units(Units.METERS_PER_SECOND)  # Primary units for speed
            radar.set_sampling_rate(SamplingRate.HZ_10000)
            radar.set_magnitude_threshold(20)

            # Enable multiple output modes
            radar.enable_json_output(True)
            radar.enable_magnitude_output(True)
            radar.enable_timestamp_output(True)

            def on_combined_detection(reading: RadarReading) -> None:
                parts = []
                if reading.speed:
                    parts.append(f"Speed: {reading.speed:.2f} m/s")
                if reading.direction:
                    parts.append(f"Dir: {reading.direction.value}")
                if reading.range_m:
                    parts.append(f"Range: {reading.range_m:.2f} m")
                if reading.magnitude:
                    parts.append(f"Mag: {reading.magnitude:.0f}")

                if parts:
                    print(f"Detection - {', '.join(parts)}")

            print("Starting combined detection...")
            radar.start_streaming(on_combined_detection)
            time.sleep(30)

    except RadarError as e:
        print(f"Radar error: {e}")


if __name__ == "__main__":
    # Display supported models
    print("Supported radar models:")
    for model in get_supported_models():
        info = get_model_info(model)
        print(f"  {model}: {info['type']} - {info['detection_range']}")

    # Run examples (uncomment to test)
    # example_doppler_usage()
    # example_fmcw_usage()
    # example_combined_usage()
