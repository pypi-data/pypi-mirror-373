"""
Timeout Feature Example

This example demonstrates the movement timeout functionality that automatically
sends zero-speed readings when no movement is detected for a specified time.

This is useful for applications that need to know when objects (like trucks)
have passed and are no longer detected by the radar.
"""

import time

from omnipresense import OutputMode, SamplingRate, Units, create_radar


def main():
    # Connect to radar sensor
    radar = create_radar("OPS243-C", "/dev/ttyACM0")

    with radar:
        # Configure sensor
        radar.set_units(Units.KILOMETERS_PER_HOUR)
        radar.set_sampling_rate(SamplingRate.HZ_1000)
        radar.enable_output_mode(OutputMode.SPEED, True)
        radar.enable_output_mode(OutputMode.DIRECTION, True)

        # Configure timeout behavior - try different values:
        # radar.set_movement_timeout(None)  # No timeout (default behavior)
        # radar.set_movement_timeout(0.0)   # Immediate timeout on empty cycles
        radar.set_movement_timeout(2.0)     # Timeout after 2 seconds of no movement

        print("Radar configured with 2-second movement timeout.")
        print("Move something in front of the sensor, then stop moving it.")
        print("You should see zero-speed readings after 2 seconds of no movement.")
        print()

        def on_detection(reading):
            timestamp = reading.timestamp
            direction = reading.direction.value if reading.direction else "?"
            speed_text = f"Speed: {reading.speed:.1f} km/h" if reading.speed else "No speed"
            
            # Indicate if this is a timeout-generated reading
            timeout_indicator = " [TIMEOUT]" if reading.raw_data == "timeout_zero_speed" else ""
            
            print(f"[{timestamp:.3f}] {speed_text}, Direction: {direction}{timeout_indicator}")
            
            # Show special handling for timeout readings
            if reading.raw_data == "timeout_zero_speed":
                print("  -> Movement has stopped (timeout triggered)")

        # Start data streaming
        radar.start_streaming(on_detection)

        # Run for 30 seconds
        print("Starting detection for 30 seconds...")
        time.sleep(30)

        print("\nDetection complete.")


def demonstration():
    """
    Demonstrates different timeout scenarios
    """
    print("=== Timeout Feature Demonstration ===")
    print()
    
    scenarios = [
        (None, "No timeout - only real radar data"),
        (0.0, "Immediate timeout - zero-speed on every empty refresh cycle"),
        (1.0, "1-second timeout - zero-speed after 1 second of no movement"),
        (3.0, "3-second timeout - zero-speed after 3 seconds of no movement"),
    ]
    
    for timeout_value, description in scenarios:
        print(f"Scenario: {description}")
        print(f"Timeout setting: {timeout_value}")
        print("Try this by uncommenting the corresponding line in main()")
        print()


if __name__ == "__main__":
    try:
        # Show available scenarios
        demonstration()
        
        # Run the main example
        main()
    except KeyboardInterrupt:
        print("\nStopped by user")
    except Exception as e:
        print(f"Error: {e}")