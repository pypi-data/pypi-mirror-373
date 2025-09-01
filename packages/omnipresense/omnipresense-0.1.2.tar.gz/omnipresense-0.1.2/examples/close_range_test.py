"""
Close Range Test

Configure the radar for very short range detection (0.5m to 5m)
This is perfect for testing by waving your hand in front of the sensor.
"""

import time

from omnipresense import SamplingRate, Units, create_radar


def main():
    radar = create_radar("OPS243-C", "/dev/ttyACM0")

    with radar:
        print("🔧 Configuring for CLOSE RANGE detection...")
        print("=" * 50)

        # Configure for close range detection
        radar.set_units(Units.METERS_PER_SECOND)
        radar.set_sampling_rate(SamplingRate.HZ_10000)

        # VERY LOW magnitude threshold for maximum sensitivity
        radar.set_magnitude_threshold(5)  # Very sensitive
        print("✅ Set magnitude threshold to 5 (very sensitive)")

        # Set VERY SHORT range filter - only detect 0.5m to 5m
        radar.set_range_filter(min_range=0.5, max_range=5.0)
        print("✅ Set range filter: 0.5m to 5.0m (very close)")

        # Set speed filter to catch even slow movements
        radar.set_speed_filter(min_speed=0.1, max_speed=10.0)
        print("✅ Set speed filter: 0.1 m/s to 10 m/s (very slow to fast)")

        # Enable all output modes
        radar.enable_json_output(True)
        radar.enable_magnitude_output(True)
        radar.enable_timestamp_output(True)

        print("\n📡 Ready for close range detection!")
        print("🖐️  Wave your hand 0.5m to 5m in front of the sensor")
        print("🚶 Move back and forth slowly within 5 meters")
        print("=" * 50)

        detection_count = 0

        def close_range_callback(reading):
            nonlocal detection_count
            detection_count += 1

            print(f"[{detection_count}] 📡 Raw: '{reading.raw_data}'")

            # Show all detected parameters
            details = []
            if reading.speed is not None:
                details.append(f"Speed: {reading.speed:.3f} m/s")
            if reading.direction:
                details.append(f"Dir: {reading.direction.value}")
            if reading.range_m is not None:
                details.append(f"Range: {reading.range_m:.2f}m")
            if reading.magnitude is not None:
                details.append(f"Signal: {reading.magnitude:.1f}")

            if details:
                print(f"    ✅ {' | '.join(details)}")

            # Special alerts for very close objects
            if reading.range_m and reading.range_m < 1.0:
                print(f"    🚨 VERY CLOSE: {reading.range_m:.2f}m!")
            elif reading.range_m and reading.range_m < 2.0:
                print(f"    ⚠️  CLOSE: {reading.range_m:.2f}m")

            print()

        # Start streaming with close-range settings
        radar.start_streaming(close_range_callback)

        # Monitor for 20 seconds with progress updates
        print("Starting close-range detection for 20 seconds...")
        for i in range(20):
            time.sleep(1)
            if i % 5 == 4:
                print(f"⏰ {i+1}s - {detection_count} detections so far")

        radar.stop_streaming()

        print("=" * 50)
        print(f"Test complete! Total detections: {detection_count}")

        if detection_count == 0:
            print("\n❌ Still no detections. Try:")
            print("1. Wave your hand directly in front (0.5-2m)")
            print("2. Move a book or object slowly back and forth")
            print("3. Walk closer to the sensor (within 3 meters)")
            print("4. Check sensor orientation - should face the area you're testing")
        else:
            print(f"\n✅ Success! Sensor detected {detection_count} movements")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Test stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
