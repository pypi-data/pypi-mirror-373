"""
Debug Usage Example

Comprehensive debugging tool for troubleshooting radar issues.
This example includes detailed logging, unit testing, and diagnostic features.

For simple usage, see basic_usage.py instead.
"""

import logging
import time

from omnipresense import SamplingRate, Units, create_radar

# Enable debug logging to see what's happening
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")


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
        # radar.set_duty_cycle(50, 0)
        # radar.set_data_precision(2)
        selected_units = Units.FEET_PER_SECOND
        print(f"Setting units to: {selected_units.value}")
        radar.set_units(selected_units)
        radar.set_sampling_rate(SamplingRate.HZ_1000)

        # Enable output modes - this is likely the missing step!
        print("Enabling output modes...")
        from omnipresense import OutputMode

        radar.enable_output_mode(OutputMode.SPEED, True)
        radar.enable_output_mode(OutputMode.DIRECTION, True)
        radar.enable_output_mode(OutputMode.MAGNITUDE, True)
        print("Output modes enabled")

        # Verify units were set correctly
        print("Checking current radar configuration...")
        try:
            current_units = radar.send_command("?u", expect_response=True)
            print(f"Current units response: {current_units}")
        except Exception as e:
            print(f"Failed to query current units: {e}")

        # Simple callback function with correct units display
        def on_detection(reading):
            # Display speed with correct units
            if reading.speed is not None:
                print(f"Detected: {reading.speed:.2f} {selected_units.value}")
            if reading.range_m is not None:
                print(f"  Range: {reading.range_m:.2f} m")
            if reading.direction:
                print(f"  Direction: {reading.direction.value}")
            if reading.magnitude:
                print(f"  Signal strength: {reading.magnitude:.0f}")
            if reading.raw_data:
                print(f"  Raw data: '{reading.raw_data}'")
            print("---")

        # Start streaming data
        print("Starting radar detection...")
        radar.start_streaming(on_detection)

        # Let it run for 10 seconds
        print("Running for 20 seconds...")
        time.sleep(20)
        radar.stop_streaming()

        print("Detection stopped.")

        # Test different units systematically
        print("\n" + "=" * 50)
        print("TESTING DIFFERENT UNITS")
        print("=" * 50)

        test_units = [
            Units.METERS_PER_SECOND,
            Units.FEET_PER_SECOND,
            Units.KILOMETERS_PER_HOUR,
            Units.MILES_PER_HOUR,
        ]

        for test_unit in test_units:
            print(f"\n--- Testing {test_unit.value} ---")
            try:
                radar.set_units(test_unit)
                # Query current units
                current_units = radar.send_command("?u", expect_response=True)
                print(f"Units query response: {current_units}")

                # Test short data collection
                readings_received = 0

                def test_callback(reading):
                    nonlocal readings_received
                    readings_received += 1
                    if readings_received <= 3:  # Only show first few readings
                        print(
                            f"  Reading {readings_received}: {reading.speed} {test_unit.value}"
                        )
                        if reading.raw_data:
                            print(f"    Raw: '{reading.raw_data}'")

                radar.start_streaming(test_callback)
                time.sleep(5)  # Test for 5 seconds
                radar.stop_streaming()

                print(f"  Total readings received: {readings_received}")

            except Exception as e:
                print(f"  ERROR with {test_unit.value}: {e}")

        print("\nAll tests completed.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
