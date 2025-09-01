"""
Ultra Sensitive Test

Maximum sensitivity settings - detects even the tiniest movements.
No filters, lowest thresholds, catches everything.
"""

import time

from omnipresense import SamplingRate, Units, create_radar


def main():
    radar = create_radar("OPS243-C", "/dev/ttyACM0")

    with radar:
        print("🔥 ULTRA SENSITIVE MODE 🔥")
        print("=" * 40)

        # Basic configuration
        radar.set_units(Units.METERS_PER_SECOND)
        radar.set_sampling_rate(SamplingRate.HZ_10000)

        # MINIMUM threshold - catches almost everything
        radar.set_magnitude_threshold(1)  # Extremely sensitive!
        print("✅ Magnitude threshold: 1 (ULTRA sensitive)")

        # NO FILTERS - catch everything
        print("✅ Removing ALL filters...")
        # Don't set any range or speed filters - catch everything!

        # Enable maximum output
        radar.enable_json_output(True)
        radar.enable_magnitude_output(True)

        print("\n🎯 This should catch ANY movement near the sensor!")
        print("🖐️  Try: wave hand, breathe deeply, small movements")
        print("=" * 40)

        any_data = False

        def ultra_sensitive_callback(reading):
            nonlocal any_data
            any_data = True

            # Show EVERYTHING
            print(f"📡 RAW: '{reading.raw_data}'")

            if reading.speed is not None and reading.speed > 0:
                print(f"    🏃 Speed: {reading.speed:.4f} m/s")
            if reading.range_m is not None:
                print(f"    📏 Range: {reading.range_m:.3f} m")
            if reading.magnitude is not None:
                print(f"    📊 Signal: {reading.magnitude:.2f}")
            if reading.direction:
                print(f"    ➡️  Direction: {reading.direction.value}")

            print()

        radar.start_streaming(ultra_sensitive_callback)

        print("Monitoring for 15 seconds...")
        print("Try ANY movement - even tiny hand movements!")

        for i in range(15):
            time.sleep(1)
            if i % 3 == 2:
                print(f"⏰ {i+1}s...")

        radar.stop_streaming()

        if not any_data:
            print("\n❌ Even ultra-sensitive mode detected nothing!")
            print("This suggests:")
            print("1. Sensor may not be streaming data")
            print("2. Sensor orientation issue")
            print("3. Hardware problem")
            print("\nTry manually sending commands to test basic communication...")
        else:
            print("\n✅ ULTRA SENSITIVE mode caught movement!")
            print("Now you can tune thresholds for normal use.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Stopped")
    except Exception as e:
        print(f"❌ Error: {e}")
