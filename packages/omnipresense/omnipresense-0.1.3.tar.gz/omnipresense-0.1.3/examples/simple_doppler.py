"""
Simple Doppler Example

Basic example for Doppler radar sensors (OPS241-A, OPS242-A, OPS243-A).
Shows speed and direction detection with magnitude filtering.
"""

import time
from omnipresense import create_radar, Units, OutputMode


def main():
    # Connect to Doppler radar sensor
    radar = create_radar("OPS243-A", "/dev/ttyACM0")

    with radar:
        # Configure for speed detection
        radar.set_units(Units.METERS_PER_SECOND)
        radar.set_magnitude_threshold(20)  # Filter weak signals

        # Enable required output modes
        radar.enable_output_mode(OutputMode.SPEED, True)
        radar.enable_output_mode(OutputMode.DIRECTION, True)
        radar.enable_output_mode(OutputMode.MAGNITUDE, True)

        print("Doppler radar ready. Wave your hand to test...")

        def on_motion(reading):
            if reading.speed and reading.speed > 0.5:
                direction = (
                    "approaching" if reading.direction.value == "+" else "receding"
                )
                magnitude = reading.magnitude or 0

                print(
                    f"Motion: {reading.speed:.2f} m/s {direction} (signal: {magnitude:.0f})"
                )

        # Start detection
        radar.start_streaming(on_motion)
        time.sleep(15)  # Run for 15 seconds

        print("Doppler detection complete.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        print(
            "Note: Make sure to use a Doppler radar model (OPS241-A, OPS242-A, or OPS243-A)"
        )

