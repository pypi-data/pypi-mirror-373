"""
Debug Streaming Example

This script helps debug why no data is being received from the radar.
It shows all raw data and uses more sensitive detection settings.
"""

import time

from omnipresense import SamplingRate, Units, create_radar


def main():
    radar = create_radar("OPS243-C", "/dev/ttyACM0")

    with radar:
        print("=== Radar Configuration ===")

        # Configure for maximum sensitivity
        radar.set_units(Units.METERS_PER_SECOND)
        radar.set_sampling_rate(SamplingRate.HZ_10000)

        # Lower thresholds for more sensitivity
        radar.set_magnitude_threshold(10)  # Lower threshold

        # Enable all output modes to see more data
        radar.enable_json_output(True)
        radar.enable_magnitude_output(True)
        radar.enable_timestamp_output(True)

        # Remove filters to catch all data
        print("Clearing all filters...")
        radar.set_speed_filter(min_speed=None, max_speed=None)  # No speed filtering
        # radar.set_range_filter(min_range=None, max_range=None)  # No range filtering

        print("Configuration complete!")
        print("=" * 50)

        # Counter to track data
        data_count = 0

        def debug_callback(reading):
            nonlocal data_count
            data_count += 1

            print(f"[{data_count}] Raw data: {reading.raw_data}")

            # Show all available data
            parts = []
            if reading.speed is not None:
                parts.append(f"Speed: {reading.speed:.3f} m/s")
            if reading.direction:
                parts.append(f"Direction: {reading.direction.value}")
            if reading.range_m is not None:
                parts.append(f"Range: {reading.range_m:.3f} m")
            if reading.magnitude is not None:
                parts.append(f"Magnitude: {reading.magnitude:.1f}")

            if parts:
                print(f"    Parsed: {' | '.join(parts)}")
            else:
                print(f"    No parsed data from: '{reading.raw_data}'")
            print()

        print("Starting sensitive data collection for 15 seconds...")
        print("Move around in front of the sensor!")
        print("Wave your hand, walk back and forth, etc.")
        print("-" * 50)

        radar.start_streaming(debug_callback)

        # Check every 3 seconds
        for i in range(5):  # 15 seconds total
            time.sleep(3)
            print(f"⏰ {(i+1)*3}s elapsed - {data_count} readings received")

        radar.stop_streaming()

        print("=" * 50)
        print(f"Total data points received: {data_count}")

        if data_count == 0:
            print("\n❌ No data received! Possible issues:")
            print("1. Nothing moving within 50-60m detection range")
            print("2. Sensor mounting/orientation issue")
            print("3. Power/communication problem")
            print("4. Try moving closer and making larger movements")
        else:
            print(f"\n✅ Sensor is working! Received {data_count} data points")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
