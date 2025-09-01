from omnipresense import Direction, Units, create_radar

radar = create_radar("OPS241-A", "/dev/ttyUSB0")

with radar:
    radar.set_units(Units.MILES_PER_HOUR)
    radar.set_speed_filter(min_speed=5, max_speed=100)  # Filter 5-100 mph
    radar.set_direction_filter(Direction.APPROACHING)  # Only approaching objects

    def speed_callback(reading):
        print(f"Vehicle: {reading.speed:.1f} mph approaching")

    radar.start_streaming(speed_callback)
