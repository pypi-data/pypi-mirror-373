# Troubleshooting Guide

This guide helps you resolve common issues when using the OmniPreSense Radar library.

## 🔧 Quick Diagnostics

Before diving into specific issues, try these quick checks:

1. **Verify hardware connection**: Check USB cable and power
2. **Confirm port name**: Use `ls /dev/tty*` (Linux/macOS) or Device Manager (Windows)
3. **Test motion detection**: Wave your hand in front of the sensor
4. **Check distance**: Ensure objects are within detection range (0.5m-25m)

## 🚨 Common Issues

### Permission Denied (Linux/macOS)

**Error:**
```bash
PermissionError: [Errno 13] Permission denied: '/dev/ttyUSB0'
```

**Solution for Linux:**
```bash
# Add your user to the dialout group
sudo usermod -a -G dialout $USER

# Log out and log back in for changes to take effect
# Or reboot your system

# Alternative: Change permissions temporarily
sudo chmod 666 /dev/ttyUSB0
```

**Solution for macOS:**
```bash
# Give permission to the serial port
sudo chmod 666 /dev/cu.usbmodem*

# Or run your Python script with sudo (not recommended)
sudo python your_script.py
```

### Port Not Found

**Error:**
```bash
FileNotFoundError: could not open port /dev/ttyUSB0: No such file or directory
```

**Solutions:**

1. **Check if device is connected**: 
   ```bash
   # Linux/macOS
   ls /dev/tty*
   
   # Look for: ttyUSB0, ttyUSB1, ttyACM0, ttyACM1
   ```

2. **Try different port names**:
   - **Linux**: `/dev/ttyUSB0`, `/dev/ttyUSB1`, `/dev/ttyACM0`, `/dev/ttyACM1`
   - **macOS**: `/dev/cu.usbmodem*`, `/dev/cu.usbserial*`
   - **Windows**: `COM3`, `COM4`, `COM5`, etc.

3. **Install drivers**: Some radar modules may need specific USB-to-serial drivers

4. **Check with system tools**:
   ```python
   # List available ports
   import serial.tools.list_ports
   for port in serial.tools.list_ports.comports():
       print(f"Port: {port.device}, Description: {port.description}")
   ```

### No Data Received

**Symptoms:**
- Radar connects successfully
- No readings in callback function
- No errors, but no output

**Solutions:**

1. **Enable output modes** (Most Important):
   ```python
   # These are REQUIRED for data transmission
   radar.enable_output_mode(OutputMode.SPEED, True)
   radar.enable_output_mode(OutputMode.DIRECTION, True)
   radar.enable_output_mode(OutputMode.MAGNITUDE, True)
   ```

2. **Create motion**: The radar only sends data when motion is detected:
   - Wave your hand in front of the sensor
   - Move objects within detection range
   - Walk back and forth in front of the sensor

3. **Check detection range**: Ensure objects are within sensor's detection range:
   - **OPS241-A/B**: 15-25m
   - **OPS243-A**: 75-100m  
   - **OPS243-C**: 50-60m

4. **Adjust sensitivity thresholds**:
   ```python
   # Lower magnitude threshold for more sensitivity
   radar.set_magnitude_threshold(10)  # Lower = more sensitive
   
   # Remove speed filters that might block data
   radar.set_speed_filter(min_speed=None, max_speed=None)
   ```

5. **Verify configuration**:
   ```python
   # Check current configuration
   config = radar.get_config()
   print(f"Units: {config.units}")
   print(f"Threshold: {config.magnitude_threshold}")
   print(f"Output modes: {config.output_modes}")
   ```

6. **Check power mode**:
   ```python
   # Ensure sensor is in active mode
   radar.set_power_mode(PowerMode.ACTIVE)
   ```

### Data Parsing Issues

**Symptoms:**
- Raw data received but not parsed correctly
- Speed/direction values are None
- Inconsistent readings

**Debug approach:**
```python
def debug_callback(reading):
    print(f"Raw data: '{reading.raw_data}'")
    print(f"Parsed - Speed: {reading.speed}, Direction: {reading.direction}")
    print(f"Range: {reading.range_m}, Magnitude: {reading.magnitude}")
    print("-" * 40)

radar.start_streaming(debug_callback)
```

**Common causes:**
1. **Wrong sensor model**: Ensure you're using the correct model string
2. **Firmware differences**: Some sensors may output different data formats
3. **Unit mismatches**: Data format changes with different units

### Windows COM Port Issues

**Problems:**
- COM port numbers change after reconnection
- "Access denied" errors
- Port appears in Device Manager but can't be opened

**Solutions:**

1. **Check Device Manager**:
   - Look for "Ports (COM & LPT)" section
   - Note the COM port number (e.g., COM3, COM4)
   - If there's a warning icon, update the driver

2. **Install proper USB drivers**:
   - Download from radar manufacturer
   - Use Windows Update to search for drivers
   - Try generic USB-to-serial drivers

3. **Close other applications**:
   ```python
   # Ensure no other software is using the port
   # Check Task Manager for competing applications
   ```

4. **Try different COM ports**:
   ```python
   for port_num in range(1, 20):
       try:
           radar = create_radar('OPS243-C', f'COM{port_num}')
           print(f"Successfully connected to COM{port_num}")
           break
       except Exception as e:
           print(f"COM{port_num}: {e}")
   ```

### Import and Installation Errors

**Error:**
```bash
ModuleNotFoundError: No module named 'omnipresense'
```

**Solutions:**

1. **Install package**:
   ```bash
   pip install omnipresense
   
   # Or for development
   pip install -e .
   ```

2. **Check Python environment**:
   ```bash
   # Verify correct Python and pip
   which python
   which pip
   
   # Check if package is installed
   pip list | grep omnipresense
   ```

3. **Virtual environment issues**:
   ```bash
   # Activate virtual environment first
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   
   # Then install
   pip install omnipresense
   ```

### Sensor-Specific Issues

#### OPS243-C (Combined Sensor)

**Issue**: Range data not appearing
```python
# Enable magnitude output for range detection
radar.enable_output_mode(OutputMode.MAGNITUDE, True)

# Use appropriate units for range
radar.set_units(Units.METERS)  # For range
# OR
radar.set_units(Units.METERS_PER_SECOND)  # For speed
```

#### OPS241-B (FMCW Only)

**Issue**: Speed data requested from range-only sensor
```python
# This sensor only provides range, not speed
def on_range_only(reading):
    if reading.range_m:
        print(f"Range: {reading.range_m:.2f}m")
    # reading.speed will always be None
```

#### OPS241-A/242-A (Doppler Only)

**Issue**: Range data requested from speed-only sensor
```python
# These sensors only provide speed/direction, not range
def on_speed_only(reading):
    if reading.speed:
        print(f"Speed: {reading.speed:.2f} m/s")
    # reading.range_m will always be None
```

## 🔍 Advanced Debugging

### Enable Debug Logging

```python
import logging

# Enable debug logging to see all communication
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

# This will show all commands sent to radar and responses received
```

### Test Basic Communication

```python
def test_basic_communication():
    radar = create_radar('OPS243-C', '/dev/ttyACM0')
    
    with radar:
        # Test basic info commands
        try:
            version = radar.send_command('??', expect_response=True)
            print(f"Firmware: {version}")
            
            board_id = radar.send_command('?P', expect_response=True)
            print(f"Board ID: {board_id}")
            
            frequency = radar.send_command('?F', expect_response=True)
            print(f"Frequency: {frequency}")
            
        except Exception as e:
            print(f"Communication error: {e}")
```

### Manual Data Capture

```python
import time
import serial

def manual_test():
    # Direct serial communication test
    ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
    
    try:
        # Send configuration commands
        ser.write(b'UK\n')  # Set units to km/h
        time.sleep(0.1)
        ser.write(b'OS\n')  # Enable speed output
        time.sleep(0.1)
        
        # Read raw data for 10 seconds
        start_time = time.time()
        while time.time() - start_time < 10:
            if ser.in_waiting > 0:
                data = ser.readline().decode('utf-8', errors='ignore').strip()
                print(f"Raw: '{data}'")
    finally:
        ser.close()
```

## 📊 Performance Issues

### Slow Data Rate

**Causes:**
- Low sampling rate
- High magnitude threshold
- Restrictive filters

**Solutions:**
```python
# Increase sampling rate
radar.set_sampling_rate(SamplingRate.HZ_10000)

# Lower magnitude threshold
radar.set_magnitude_threshold(10)

# Remove restrictive filters
radar.set_speed_filter(min_speed=None, max_speed=None)
```

### High CPU Usage

**Causes:**
- Too frequent callbacks
- Heavy processing in callback

**Solutions:**
```python
# Limit callback frequency
callback_count = 0
def throttled_callback(reading):
    global callback_count
    callback_count += 1
    if callback_count % 10 == 0:  # Process every 10th reading
        process_reading(reading)

# Or use threading for heavy processing
import threading
from queue import Queue

data_queue = Queue()

def fast_callback(reading):
    data_queue.put(reading)

def background_processor():
    while True:
        reading = data_queue.get()
        # Heavy processing here
        process_reading(reading)

threading.Thread(target=background_processor, daemon=True).start()
```

## 🆘 Getting Further Help

If these solutions don't resolve your issue:

1. **Hardware verification**: Test with OmniPreSense's official software first
2. **Check specifications**: Verify your radar model capabilities
3. **Review examples**: Look at working examples in the `examples/` directory
4. **GitHub Issues**: Search existing issues or create a new one
5. **Documentation**: Check the API documentation for your specific use case

### Information to Include in Bug Reports

When reporting issues, please include:

- **Hardware**: Radar model (e.g., OPS243-C)
- **OS**: Operating system and version
- **Python**: Python version and virtual environment info
- **Library**: OmniPreSense library version
- **Code**: Minimal reproduction example
- **Error**: Complete error message and stack trace
- **Attempts**: What you've already tried

Example bug report format:
```
**Hardware:** OPS243-C
**OS:** Ubuntu 22.04 
**Python:** 3.9.7 (venv)
**Library:** omnipresense 1.0.0
**Issue:** No data received despite motion

**Code:**
```python
# Your minimal reproduction code here
```

**Error:** 
No error messages, but callback never fires

**Attempted:**
- Verified USB connection
- Tried different ports
- Enabled output modes
- Lowered magnitude threshold
```

This helps maintainers diagnose and fix issues quickly.