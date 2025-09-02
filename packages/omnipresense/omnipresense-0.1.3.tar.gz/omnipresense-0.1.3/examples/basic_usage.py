"""
Basic Usage Example

A minimal example showing how to get started with OmniPreSense radar sensors.
This example uses kilometers per hour and shows speed, direction, and distance detection.
"""

import time

from omnipresense import OutputMode, PowerMode, SamplingRate, Units, create_radar


def main():
    # Connect to radar sensor
    radar = create_radar("OPS243-C", "/dev/ttyACM0")

    with radar:
        # Configure sensor for speed detection in km/h
        radar.set_power_mode(PowerMode.ACTIVE)
        radar.set_units(Units.KILOMETERS_PER_HOUR)
        radar.set_data_precision(2)
        radar.set_sampling_rate(SamplingRate.HZ_1000)
        radar.set_duty_cycle(5, 0)

        # Enable output modes (required for data transmission)
        radar.enable_output_mode(OutputMode.SPEED, True)
        radar.enable_output_mode(OutputMode.DIRECTION, True)
        radar.enable_output_mode(OutputMode.MAGNITUDE, True)

        print("Radar configured. Move something in front of the sensor...")

        # Define callback for radar readings
        def on_detection(reading):
            print(f"Raw data: '{reading.raw_data}'")
            direction = reading.direction.value if reading.direction else "?"
            distance = f", Distance: {reading.range_m:.1f}m" if reading.range_m else ""
            speed_text = (
                f"Speed: {reading.speed:.1f} km/h" if reading.speed else "No speed"
            )
            print(f"{speed_text}, Direction: {direction}{distance}")

        # Start data streaming
        radar.start_streaming(on_detection)

        # Run for 10 seconds
        time.sleep(10)

        print("Detection complete.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
