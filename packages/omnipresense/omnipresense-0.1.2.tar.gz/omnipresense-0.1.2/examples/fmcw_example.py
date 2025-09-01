"""
FMCW Radar Example - Range Detection

Demonstrates how to use OPS241-B FMCW radar for range measurements.
"""

import time

from omnipresense import Units, create_radar


def main():
    # Create FMCW radar sensor
    radar = create_radar("OPS241-B", "/dev/ttyUSB0")

    with radar:
        # Configure for range measurement
        radar.set_units(Units.METERS)
        radar.set_magnitude_threshold(150)
        radar.set_range_filter(min_range=0.5, max_range=15.0)

        # Enable JSON output for structured data
        radar.enable_json_output(True)

        def range_callback(reading):
            if reading.range_m:
                print(
                    f"Object detected at {reading.range_m:.2f}m "
                    f"(signal strength: {reading.magnitude:.0f})"
                )

        print("Starting range detection... (press Ctrl+C to stop)")
        radar.start_streaming(range_callback)

        try:
            time.sleep(30)  # Run for 30 seconds
        except KeyboardInterrupt:
            print("\nStopping radar...")


if __name__ == "__main__":
    main()
