# OmniPreSense Radar

<div align="center">

[![PyPI version](https://badge.fury.io/py/omnipresense.svg)](https://badge.fury.io/py/omnipresense)
[![Python versions](https://img.shields.io/pypi/pyversions/omnipresense.svg)](https://pypi.org/project/omnipresense/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Downloads](https://pepy.tech/badge/omnipresense)](https://pepy.tech/project/omnipresense)

**A comprehensive, type-safe Python interface for OmniPreSense radar sensors**

_Supports all OPS241/OPS242/OPS243 radar models with full API coverage_

> **⚠️ DISCLAIMER**: This is an **unofficial**, community-developed library. The
> author is **not affiliated** with OmniPreSense Corp. This library provides a
> Python interface for OmniPreSense radar sensors but is not endorsed or
> supported by the company.

[🚀 Quick Start](#quick-start) • [📚 Examples](#examples) • [🛠️ Troubleshooting](TROUBLESHOOTING.md) • [🤝 Contributing](CONTRIBUTING.md)

</div>

---

## ✨ Features

- 📋 **Complete API Coverage** - All commands from the [official API documentation](https://omnipresense.com/wp-content/uploads/2019/10/AN-010-Q_API_Interface.pdf)
- 🔒 **Type-Safe** - Full typing support with comprehensive enums and data classes
- 📡 **Multiple Sensor Support** - Doppler (-A), FMCW (-B), and combined (-C) sensor types
- 🧵 **Thread-Safe** - Robust serial communication with proper synchronization
- 🔧 **Context Managers** - Automatic resource cleanup with `with` statements
- 📊 **Rich Data Structures** - Structured radar readings with timestamps and metadata
- ⚡ **High Performance** - Efficient data streaming with configurable callbacks
- 🛡️ **Error Handling** - Comprehensive exception hierarchy with detailed messages

## 📡 Supported Models

| Model        | Type     | Features                            | Detection Range | Max Speed |
| ------------ | -------- | ----------------------------------- | --------------- | --------- |
| **OPS241-A** | Doppler  | Motion, Speed, Direction, Magnitude | 20-25m          | 31.1 m/s  |
| **OPS242-A** | Doppler  | Enhanced sensitivity                | 20-25m          | 31.1 m/s  |
| **OPS243-A** | Doppler  | Advanced + Range\*                  | 75-100m         | 31.1 m/s  |
| **OPS241-B** | FMCW     | Range, Magnitude                    | 15-20m          | N/A       |
| **OPS243-C** | Combined | All features                        | 50-60m          | 31.1 m/s  |

\*Range measurement pending in firmware

## 🚀 Quick Start

### Installation

```bash
pip install omnipresense
```

### Basic Usage

```python
from omnipresense import create_radar, Units, OutputMode
import time

# Create radar sensor
radar = create_radar('OPS243-C', '/dev/ttyACM0')

# Use context manager for automatic cleanup
with radar:
    # Configure sensor
    radar.set_units(Units.KILOMETERS_PER_HOUR)
    
    # Enable output modes (required for data transmission)
    radar.enable_output_mode(OutputMode.SPEED, True)
    radar.enable_output_mode(OutputMode.DIRECTION, True)
    radar.enable_output_mode(OutputMode.MAGNITUDE, True)

    # Define callback for radar data
    def on_detection(reading):
        if reading.speed and reading.speed > 1.0:
            direction = reading.direction.value if reading.direction else "?"
            distance = f", Distance: {reading.range_m:.1f}m" if reading.range_m else ""
            print(f"Speed: {reading.speed:.1f} km/h, Direction: {direction}{distance}")

    # Start streaming data
    print("Move something in front of the radar...")
    radar.start_streaming(on_detection)
    time.sleep(10)  # Stream for 10 seconds
```

> **Important**: Always enable appropriate output modes (`OutputMode.SPEED`, `OutputMode.DIRECTION`, `OutputMode.MAGNITUDE`) for data transmission. Without these, the radar will not send any data.

## 📋 Requirements

- **Python**: 3.8.1+
- **Dependencies**: `pyserial` >= 3.4

## 📁 Examples

The [`examples/`](examples/) directory contains working scripts for different use cases:

- **[`basic_usage.py`](examples/basic_usage.py)** - Simple km/h speed detection with distance
- **[`basic_usage_raw.py`](examples/basic_usage_raw.py)** - PySerial version showing raw protocol
- **[`simple_doppler.py`](examples/simple_doppler.py)** - Doppler radar with direction detection
- **[`simple_range.py`](examples/simple_range.py)** - FMCW range measurement
- **[`combined_example.py`](examples/combined_example.py)** - OPS243-C combined features
- **[`debug_usage.py`](examples/debug_usage.py)** - Comprehensive debugging tool
- **[`raw_data_test.py`](examples/raw_data_test.py)** - Raw data inspection utility

Run any example:
```bash
python examples/basic_usage.py
```

## ⚙️ Key Configuration

### Output Modes (Required)
```python
# Enable data transmission (essential!)
radar.enable_output_mode(OutputMode.SPEED, True)
radar.enable_output_mode(OutputMode.DIRECTION, True)
radar.enable_output_mode(OutputMode.MAGNITUDE, True)
```

### Units and Sensitivity
```python
# Set measurement units
radar.set_units(Units.KILOMETERS_PER_HOUR)  # or METERS_PER_SECOND, MILES_PER_HOUR

# Adjust sensitivity (lower = more sensitive)
radar.set_magnitude_threshold(20)  # Default: 20, Range: 1-200+
```

### Filtering
```python
# Filter readings by speed and range
radar.set_speed_filter(min_speed=1.0, max_speed=50.0)
radar.set_range_filter(min_range=0.5, max_range=25.0)
```

## 📊 Data Structure

Each radar reading provides:

```python
@dataclass
class RadarReading:
    timestamp: float                    # Unix timestamp
    speed: Optional[float]              # Speed in configured units
    direction: Optional[Direction]      # APPROACHING/RECEDING
    range_m: Optional[float]           # Range in meters
    magnitude: Optional[float]         # Signal strength
    raw_data: Optional[str]            # Original data string
```

## 🛡️ Error Handling

```python
from omnipresense import RadarError, RadarConnectionError

try:
    with create_radar('OPS243-C', '/dev/ttyACM0') as radar:
        radar.set_units(Units.METERS_PER_SECOND)
        # ... use radar

except RadarConnectionError:
    print("Could not connect to radar sensor")
except RadarError as e:
    print(f"Radar error: {e}")
```

## 🔧 Quick Troubleshooting

### No Data Received?
1. **Enable output modes**: `radar.enable_output_mode(OutputMode.SPEED, True)`
2. **Create motion**: Wave your hand in front of the sensor
3. **Check distance**: Ensure objects are within 0.5m-25m range
4. **Lower threshold**: `radar.set_magnitude_threshold(10)`

### Permission Denied (Linux)?
```bash
sudo usermod -a -G dialout $USER  # Add user to dialout group
# Then logout and login again
```

### Port Not Found?
- **Linux**: Try `/dev/ttyUSB0`, `/dev/ttyACM0`, `/dev/ttyACM1`
- **macOS**: Try `/dev/cu.usbmodem*`, `/dev/cu.usbserial*`  
- **Windows**: Try `COM3`, `COM4`, `COM5`, etc.

**Need more help?** See the comprehensive [**Troubleshooting Guide**](TROUBLESHOOTING.md).

## 📚 Documentation & Support

- **[Troubleshooting Guide](TROUBLESHOOTING.md)** - Detailed issue resolution
- **[Contributing Guide](CONTRIBUTING.md)** - Development and contribution info
- **[Examples Directory](examples/)** - Working code examples
- **[GitHub Issues](https://github.com/yourusername/OmnipresenseRadar/issues)** - Bug reports and feature requests

## 🤝 Contributing

We welcome contributions! Please see our [**Contributing Guide**](CONTRIBUTING.md) for:
- Development environment setup
- Code quality standards
- Testing guidelines  
- Pull request process

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## ⚖️ Legal Notice

This project is an **independent, unofficial** implementation developed by the community. It is **not affiliated with, endorsed by, or supported by OmniPreSense Corp.**

- **Trademark**: "OmniPreSense" is a trademark of OmniPreSense Corp.
- **Hardware**: This library is designed to work with OmniPreSense radar sensors
- **Support**: For hardware issues, contact [OmniPreSense directly](https://omnipresense.com/support/). For library issues, use our GitHub Issues.
- **Warranty**: This software comes with no warranty. Use at your own risk.

---

<div align="center">

**⭐ Star this repo if it helps you build amazing radar applications! ⭐**

_Made with ❤️ for the radar sensing community_

</div>