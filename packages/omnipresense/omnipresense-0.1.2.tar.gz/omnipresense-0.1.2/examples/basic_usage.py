"""
Basic Usage Example

Simple example showing basic radar setup and data streaming.
"""

import time

from omnipresense import SamplingRate, Units, create_radar


def main():
    # Create radar sensor - will automatically detect capabilities
    radar = create_radar("OPS243-C", "/dev/ttyACM0")

    # Use context manager for automatic cleanup
    with radar:
        # Get sensor information
        info = radar.get_sensor_info()
        print(f"Connected to: {info.model}")
        print(f"Firmware: {info.firmware_version}")
        print(f"Detection range: {info.detection_range}")
        print(f"Features: Doppler={info.has_doppler}, FMCW={info.has_fmcw}")
        print("-" * 50)

        # Configure sensor
        radar.set_units(Units.METERS_PER_SECOND)
        radar.set_sampling_rate(SamplingRate.HZ_10000)
        radar.set_magnitude_threshold(20)

        # Simple callback function
        def on_detection(reading):
            if reading.speed and reading.speed > 1.0:  # Filter out slow movements
                print(f"Detected: {reading.speed:.2f} m/s")
                if reading.direction:
                    print(f"  Direction: {reading.direction.value}")
                if reading.magnitude:
                    print(f"  Signal strength: {reading.magnitude:.0f}")
                print()

        # Start streaming data
        print("Starting radar detection...")
        radar.start_streaming(on_detection)

        # Let it run for 10 seconds
        time.sleep(10)

        print("Detection stopped.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
