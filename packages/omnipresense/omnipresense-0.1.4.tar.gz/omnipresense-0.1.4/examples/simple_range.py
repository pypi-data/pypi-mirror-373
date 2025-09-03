"""
Simple Range Example

Basic example for FMCW radar sensors (OPS241-B, OPS243-C).
Shows distance measurement and object detection.
"""

import time
from omnipresense import create_radar, Units, OutputMode


def main():
    # Connect to FMCW radar sensor
    radar = create_radar("OPS241-B", "/dev/ttyACM0")

    with radar:
        # Configure for range detection in meters
        radar.set_units(Units.METERS)

        # Enable range output (FMCW sensors detect range, not speed)
        radar.enable_output_mode(OutputMode.MAGNITUDE, True)

        print("Range radar ready. Place objects at different distances...")

        def on_range_detection(reading):
            if reading.range_m and reading.range_m > 0.1:  # Filter very close readings
                magnitude = reading.magnitude or 0
                print(
                    f"Object detected at {reading.range_m:.2f}m (signal: {magnitude:.0f})"
                )

        # Start range detection
        radar.start_streaming(on_range_detection)
        time.sleep(15)  # Run for 15 seconds

        print("Range detection complete.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        print("Note: Use FMCW radar models (OPS241-B) or combined models (OPS243-C)")

