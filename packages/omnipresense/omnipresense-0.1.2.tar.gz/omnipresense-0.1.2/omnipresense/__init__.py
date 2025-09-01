"""
OmniPreSense Radar Sensor Interface

A comprehensive, type-safe Python interface for OmniPreSense radar sensors.
Supports all OPS241/OPS242/OPS243 radar models with full API coverage.

Example:
    from omnipresense import create_radar, Units, SamplingRate

    radar = create_radar('OPS243-A', '/dev/ttyACM0')
    with radar:
        radar.set_units(Units.METERS_PER_SECOND)
        radar.set_sampling_rate(SamplingRate.HZ_10000)
        # ... use radar
"""

from .radar import (  # Factory function (main entry point); Enums; Data classes; Exception classes; Utility functions; Sensor classes (for advanced usage)
    Direction,
    OPS241A_DopplerRadar,
    OPS241B_FMCWRadar,
    OPS242A_DopplerRadar,
    OPS243A_DopplerRadar,
    OPS243C_CombinedRadar,
    OPSRadarSensor,
    OutputMode,
    PowerMode,
    RadarCommandError,
    RadarConfig,
    RadarConnectionError,
    RadarError,
    RadarReading,
    RadarTimeoutError,
    RadarValidationError,
    SamplingRate,
    SensorInfo,
    SensorType,
    Units,
    create_radar,
    get_model_info,
    get_supported_models,
)

__version__ = "0.1.0"
__author__ = "Oskar Graeb"
__email__ = "graeb.oskar@gmail.com"
__license__ = "MIT"

__all__ = [
    # Main factory function
    "create_radar",
    # Enums
    "Units",
    "SamplingRate",
    "Direction",
    "PowerMode",
    "OutputMode",
    "SensorType",
    # Data classes
    "RadarReading",
    "SensorInfo",
    "RadarConfig",
    # Exceptions
    "RadarError",
    "RadarConnectionError",
    "RadarCommandError",
    "RadarValidationError",
    "RadarTimeoutError",
    # Utility functions
    "get_supported_models",
    "get_model_info",
    # Sensor classes
    "OPSRadarSensor",
    "OPS241A_DopplerRadar",
    "OPS242A_DopplerRadar",
    "OPS243A_DopplerRadar",
    "OPS241B_FMCWRadar",
    "OPS243C_CombinedRadar",
]
