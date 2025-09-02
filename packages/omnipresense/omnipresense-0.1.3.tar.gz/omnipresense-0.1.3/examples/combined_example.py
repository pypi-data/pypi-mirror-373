"""
Combined Radar Example - Speed + Range Detection

Demonstrates how to use OPS243-C combined FMCW & Doppler radar for
simultaneous speed and range measurements.
"""

import time

from omnipresense import Direction, SamplingRate, Units, OutputMode, create_radar


def main():
    # Create combined radar sensor
    radar = create_radar("OPS243-C", "/dev/ttyUSB0")

    with radar:
        # Configure for both speed and range
        radar.set_units(Units.METERS_PER_SECOND)
        radar.set_sampling_rate(SamplingRate.HZ_10000)
        radar.set_magnitude_threshold(20)

        # Set up filters
        radar.set_speed_filter(min_speed=0.5, max_speed=30.0)
        radar.set_range_filter(min_range=1.0, max_range=50.0)

        # Enable required output modes for combined detection
        radar.enable_output_mode(OutputMode.SPEED, True)
        radar.enable_output_mode(OutputMode.DIRECTION, True) 
        radar.enable_output_mode(OutputMode.MAGNITUDE, True)
        # Enable enhanced output modes
        radar.enable_json_output(True)
        radar.enable_magnitude_output(True)
        radar.enable_timestamp_output(True)

        def combined_callback(reading):
            data_parts = []

            if reading.speed:
                direction_str = ""
                if reading.direction == Direction.APPROACHING:
                    direction_str = " (approaching)"
                elif reading.direction == Direction.RECEDING:
                    direction_str = " (receding)"
                data_parts.append(f"Speed: {reading.speed:.2f} m/s{direction_str}")

            if reading.range_m:
                data_parts.append(f"Range: {reading.range_m:.2f} m")

            if reading.magnitude:
                data_parts.append(f"Signal: {reading.magnitude:.0f}")

            if data_parts:
                timestamp_str = f"[{reading.timestamp:.3f}]"
                print(f"{timestamp_str} {' | '.join(data_parts)}")

        print("Starting combined detection... (press Ctrl+C to stop)")
        radar.start_streaming(combined_callback)

        try:
            time.sleep(60)  # Run for 1 minute
        except KeyboardInterrupt:
            print("\nStopping radar...")


if __name__ == "__main__":
    main()
