# OmniPreSense Radar

<div align="center">

[![PyPI version](https://badge.fury.io/py/omnipresense.svg)](https://badge.fury.io/py/omnipresense)
[![Python versions](https://img.shields.io/pypi/pyversions/omnipresense.svg)](https://pypi.org/project/omnipresense/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Downloads](https://pepy.tech/badge/omnipresense)](https://pepy.tech/project/omnipresense)
[![Build Status](https://github.com/yourusername/OmnipresenseRadar/workflows/CI/badge.svg)](https://github.com/yourusername/OmnipresenseRadar/actions)

**A comprehensive, type-safe Python interface for OmniPreSense radar sensors**

_Supports all OPS241/OPS242/OPS243 radar models with full API coverage_

> **⚠️ DISCLAIMER**: This is an **unofficial**, community-developed library. The
> author is **not affiliated** with OmniPreSense Corp. This library provides a
> Python interface for OmniPreSense radar sensors but is not endorsed or
> supported by the company.

[🚀 Quick Start](#quick-start) • [📚 Documentation](#documentation) •
[💡 Examples](#examples) • [🤝 Contributing](#contributing)

</div>

---

## ✨ Features

- 📋 **Complete API Coverage** - All commands from the
  [official API documentation](https://omnipresense.com/wp-content/uploads/2019/10/AN-010-Q_API_Interface.pdf)
- 🔒 **Type-Safe** - Full typing support with comprehensive enums and data
  classes
- 📡 **Multiple Sensor Support** - Doppler (-A), FMCW (-B), and combined (-C)
  sensor types
- 🧵 **Thread-Safe** - Robust serial communication with proper synchronization
- 🔧 **Context Managers** - Automatic resource cleanup with `with` statements
- 📊 **Rich Data Structures** - Structured radar readings with timestamps and
  metadata
- ⚡ **High Performance** - Efficient data streaming with configurable callbacks
- 🛡️ **Error Handling** - Comprehensive exception hierarchy with detailed
  messages
- 📚 **Well Documented** - Extensive docstrings and usage examples

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
from omnipresense import create_radar, Units, SamplingRate
import time

# Create radar sensor
radar = create_radar('OPS243-C', '/dev/ttyACM0')

# Use context manager for automatic cleanup
with radar:
    # Configure sensor
    radar.set_units(Units.METERS_PER_SECOND)
    radar.set_sampling_rate(SamplingRate.HZ_10000)
    radar.set_magnitude_threshold(20)

    # Define callback for radar data
    def on_detection(reading):
        if reading.speed and reading.speed > 1.0:
            print(f"Speed: {reading.speed:.2f} m/s")
            print(f"Direction: {reading.direction.value}")
            print(f"Magnitude: {reading.magnitude}")

    # Start streaming data
    radar.start_streaming(on_detection)
    time.sleep(10)  # Stream for 10 seconds
```

## 📋 Requirements

- **Python**: 3.8.1+
- **Dependencies**:
  - `pyserial` >= 3.4

## 💡 Examples

### Basic Usage

```python
from omnipresense import create_radar, Units

radar = create_radar('OPS243-C', '/dev/ttyACM0')

with radar:
    radar.set_units(Units.METERS_PER_SECOND)

    def on_detection(reading):
        if reading.speed:
            print(f"Speed: {reading.speed:.2f} m/s")
        if reading.range_m:
            print(f"Range: {reading.range_m:.2f} m")

    radar.start_streaming(on_detection)
```

> 📁 **More Examples**: See the [`examples/`](examples/) directory for
> additional scripts including Doppler-only sensors, FMCW sensors, debugging
> tools, and advanced configurations.

## ⚙️ Advanced Configuration

### Power Management

```python
from omnipresense import PowerMode

# Set power modes for battery optimization
radar.set_power_mode(PowerMode.IDLE)     # Low power mode
radar.set_duty_cycle(100, 1000)          # 100ms active, 1000ms sleep
```

### Data Output Formats

```python
from omnipresense import OutputMode

# Enable multiple output modes
radar.enable_json_output(True)           # JSON format
radar.enable_magnitude_output(True)      # Signal strength
radar.enable_timestamp_output(True)      # Timestamps
radar.set_data_precision(3)              # 3 decimal places
```

### Filtering and Thresholds

```python
# Advanced filtering
radar.set_speed_filter(min_speed=0.5, max_speed=50.0)
radar.set_range_filter(min_range=2.0, max_range=25.0)
radar.set_magnitude_threshold(50)        # Noise filtering
```

## 📊 Data Structure

The `RadarReading` object contains:

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

## ℹ️ Sensor Information

```python
# Get comprehensive sensor info
info = radar.get_sensor_info()
print(f"Model: {info.model}")
print(f"Firmware: {info.firmware_version}")
print(f"Detection Range: {info.detection_range}")
print(f"Features: Doppler={info.has_doppler}, FMCW={info.has_fmcw}")

# Query specific details
print(f"Frequency: {radar.get_frequency()} Hz")
print(f"Board ID: {radar.get_board_id()}")
```

## 🛡️ Error Handling

```python
from omnipresense import (
    RadarError, RadarConnectionError,
    RadarCommandError, RadarValidationError
)

try:
    with create_radar('OPS241-A', '/dev/ttyUSB0') as radar:
        radar.set_units(Units.METERS_PER_SECOND)
        # ... use radar

except RadarConnectionError:
    print("Could not connect to radar sensor")
except RadarValidationError as e:
    print(f"Configuration error: {e}")
except RadarError as e:
    print(f"Radar error: {e}")
```

## 📚 Documentation

- **[API Reference](docs/api.md)** - Complete method documentation
- **[Hardware Guide](docs/hardware.md)** - Sensor setup and wiring
- **[Examples](examples/)** - Complete working examples
- **[Troubleshooting](docs/troubleshooting.md)** - Common issues and solutions

## 🔧 Development

### Setup Development Environment

```bash
git clone https://github.com/yourusername/OmnipresenseRadar.git
cd OmnipresenseRadar

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=omnipresense

# Run specific test file
pytest tests/test_doppler_radar.py -v
```

### Code Quality

```bash
# Run all pre-commit hooks on all files
pre-commit run --all-files

# Format code manually (if needed)
black omnipresense/ tests/

# Type checking
mypy omnipresense/

# Linting with ruff
ruff check omnipresense/ tests/
ruff format omnipresense/ tests/

# Security scanning
bandit -r omnipresense/
```

### Pre-commit Hooks

This project uses pre-commit hooks to ensure code quality. The following checks
run automatically on each commit:

- **Code Formatting**: Black, isort for consistent style
- **Linting**: Ruff for code quality and style issues
- **Type Checking**: MyPy for static type analysis
- **Security**: Bandit for security vulnerability scanning
- **Dependencies**: Safety for known security vulnerabilities
- **Documentation**: Pydocstyle for docstring conventions
- **Import Management**: Autoflake removes unused imports
- **Syntax Upgrades**: PyUpgrade modernizes Python syntax
- **Commit Messages**: Conventional commit format validation

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md)
for details.

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Ways to Contribute

- 🐛 **Bug Reports** - Found an issue? Let us know!
- 💡 **Feature Requests** - Have ideas? We'd love to hear them!
- 📚 **Documentation** - Help improve our docs
- 🧪 **Testing** - Add tests for better coverage
- 💻 **Code** - Fix bugs or add new features

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE)
file for details.

## 🙏 Acknowledgments

- **[OmniPreSense](https://omnipresense.com/)** for creating excellent radar
  sensors and comprehensive documentation
- **Contributors** who help improve this library
- **Community** for feedback and bug reports

## ⚖️ Legal Notice

This project is an **independent, unofficial** implementation developed by the
community. It is **not affiliated with, endorsed by, or supported by
OmniPreSense Corp.**

- **Trademark**: "OmniPreSense" is a trademark of OmniPreSense Corp.
- **Hardware**: This library is designed to work with OmniPreSense radar sensors
- **Support**: For hardware issues, contact
  [OmniPreSense directly](https://omnipresense.com/support/). For library
  issues, use our GitHub Issues.
- **Warranty**: This software comes with no warranty. Use at your own risk.

## 🔧 Troubleshooting

### Common Issues

#### Permission Denied (Linux/macOS)

```bash
PermissionError: [Errno 13] Permission denied: '/dev/ttyUSB0'
```

**Solution for Linux:**

```bash
# Add your user to the dialout group
sudo usermod -a -G dialout $USER

# Log out and log back in for changes to take effect
# Or reboot your system
```

**Solution for macOS:**

```bash
# Give permission to the serial port
sudo chmod 666 /dev/cu.usbmodem*
# Or run your Python script with sudo (not recommended)
```

#### Port Not Found

```bash
FileNotFoundError: could not open port /dev/ttyUSB0: No such file or directory
```

**Solutions:**

1. **Check if device is connected**: `ls /dev/tty*` (Linux/macOS) or check
   Device Manager (Windows)
2. **Try different port names**:
   - Linux: `/dev/ttyUSB0`, `/dev/ttyUSB1`, `/dev/ttyACM0`, `/dev/ttyACM1`
   - macOS: `/dev/cu.usbmodem*`, `/dev/cu.usbserial*`
   - Windows: `COM3`, `COM4`, `COM5`, etc.
3. **Install drivers**: Some radar modules may need specific USB-to-serial
   drivers

#### No Data Received

```python
# Radar connects but no readings in callback
```

**Solutions:**

1. **Check detection range**: Ensure objects are within sensor's detection range
2. **Adjust thresholds**: Lower magnitude threshold for more sensitivity
3. **Check power mode**: Ensure sensor is in active mode
4. **Verify configuration**: Check units, sampling rate, and filters

#### Import Errors

```bash
ModuleNotFoundError: No module named 'omnipresense'
```

**Solutions:**

1. **Install package**: `pip install omnipresense`
2. **Development install**: `pip install -e .` (from project root)
3. **Check Python environment**: Ensure you're using the correct virtual
   environment

#### Windows COM Port Issues

On Windows, you may need to:

1. Check Device Manager for the correct COM port number
2. Install proper USB drivers for your radar module
3. Try different COM ports (COM3, COM4, COM5, etc.)

### Getting Help

If you're still experiencing issues:

1. **Check sensor specifications**: Verify your radar model and its capabilities
2. **Review examples**: Look at the examples in the `examples/` directory
3. **Enable debug logging**: Add logging to see detailed communication

   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

4. **Hardware verification**: Test with OmniPreSense's official software first

## 🆘 Support

- **GitHub Issues**:
  [Report bugs or request features](https://github.com/yourusername/OmnipresenseRadar/issues)
- **Documentation**:
  [Read the full docs](https://OmnipresenseRadar.readthedocs.io/)
- **Email**: <graeb.oskar@gmail.com>

---

<div align="center">

**⭐ Star this repo if it helps you build amazing radar applications! ⭐**

_Made with ❤️ for the radar sensing community_

</div>
