# Examples

This directory contains example scripts demonstrating how to use the
OmniPreSense radar library.

## Running Examples

Make sure you have the library installed:

```bash
pip install -e .
```

Then run any example:

```bash
python examples/basic_usage.py
```

**Note**: You'll need to update the serial port path in each example to match
your system (e.g., `/dev/ttyUSB0`, `/dev/ttyACM0`, or `COM3` on Windows).

## Available Examples

### `basic_usage.py`

Simple example showing basic radar setup and data streaming. Good starting point
for beginners.

### `doppler_example.py`

Demonstrates Doppler radar usage for vehicle speed detection with filtering.

### `fmcw_example.py`

Shows how to use FMCW radar for range detection and distance measurement.

### `combined_example.py`

Advanced example using combined FMCW + Doppler radar for simultaneous speed and
range detection.

## Hardware Setup

1. Connect your OmniPreSense radar sensor to your computer via USB
2. Find the correct serial port:
   - Linux: Usually `/dev/ttyUSB0` or `/dev/ttyACM0`
   - macOS: Usually `/dev/cu.usbmodem*` or `/dev/cu.usbserial*`
   - Windows: Usually `COM3`, `COM4`, etc.
3. Update the port name in the example code
4. Run the example

## Troubleshooting

- **Permission denied**: On Linux/macOS, you may need to add your user to the
  `dialout` group or use `sudo`
- **Port not found**: Check that the radar is connected and the correct port is
  specified
- **No data**: Ensure the radar has a clear line of sight and objects are within
  detection range
