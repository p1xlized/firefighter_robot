import time

try:
    import RPi.GPIO as GPIO
except (ImportError, RuntimeError):
    GPIO = None

RELAY_PIN = 17
gpio_initialized = False


def _setup_gpio() -> None:
    global gpio_initialized
    if GPIO is None:
        raise RuntimeError("RPi.GPIO is required on the Raspberry Pi")
    if gpio_initialized:
        return
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RELAY_PIN, GPIO.OUT, initial=GPIO.LOW)
    gpio_initialized = True


def turn_on_pump_motor() -> None:
    _setup_gpio()
    GPIO.output(RELAY_PIN, GPIO.HIGH)
    print("Motor ON")


def turn_off_pump_motor() -> None:
    _setup_gpio()
    GPIO.output(RELAY_PIN, GPIO.LOW)
    print("Motor OFF")


def test_pump() -> None:
    _setup_gpio()
    try:
        # Main loop
        while True:
            turn_on_pump_motor()
            time.sleep(1)  # Run the motor
            turn_off_pump_motor()
            time.sleep(2)  # Wait before turning on again
    except KeyboardInterrupt:
        # Clean up GPIO on keyboard interrupt
        GPIO.cleanup()
        print("\nGPIO cleaned up. Exiting.")
