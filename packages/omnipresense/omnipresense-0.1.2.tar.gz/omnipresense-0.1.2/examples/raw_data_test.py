"""
Raw Data Test

Shows all raw data coming from the radar without any filtering or parsing.
This helps verify if the sensor is sending any data at all.
"""

import time

from omnipresense import create_radar


def main():
    radar = create_radar("OPS243-C", "/dev/ttyACM0")

    with radar:
        print("🔍 Raw data monitor - showing ALL data from sensor")
        print("Move around in front of the sensor...")
        print("=" * 60)

        data_received = False

        def raw_callback(reading):
            nonlocal data_received
            data_received = True

            # Show the raw data string exactly as received
            print(f"📡 Raw: '{reading.raw_data}' | Timestamp: {reading.timestamp:.3f}")

            # Show what got parsed
            if reading.speed or reading.range_m or reading.magnitude:
                parsed = []
                if reading.speed:
                    parsed.append(f"speed={reading.speed}")
                if reading.range_m:
                    parsed.append(f"range={reading.range_m}")
                if reading.magnitude:
                    parsed.append(f"mag={reading.magnitude}")
                if reading.direction:
                    parsed.append(f"dir={reading.direction.value}")
                print(f"    ✅ Parsed: {', '.join(parsed)}")
            else:
                print("    ⚠️  No data parsed from raw string")
            print()

        # Minimal configuration - just start streaming
        radar.start_streaming(raw_callback)

        # Monitor for 20 seconds
        for i in range(20):
            time.sleep(1)
            if i % 5 == 4:  # Every 5 seconds
                print(f"⏰ {i+1} seconds elapsed...")

        radar.stop_streaming()

        if not data_received:
            print("\n❌ No raw data received from sensor!")
            print("The sensor may not be sending any data.")
            print("Try:")
            print("1. Check if sensor is powered on")
            print("2. Move objects within detection range (50-60m)")
            print("3. Make sure sensor has clear line of sight")
        else:
            print("\n✅ Sensor is sending data!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
