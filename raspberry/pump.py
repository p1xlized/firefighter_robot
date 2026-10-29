import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
relay_pin = 17
GPIO.setup(relay_pin, GPIO.OUT)

def turn_on_motor():
    GPIO.output(relay_pin, GPIO.HIGH)
    print("Motor ON")


def turn_off_motor():
    GPIO.output(relay_pin, GPIO.LOW)
    print("Motor OFF")

def test_pump():

    try:
        # Main loop
        while True:
            turn_on_motor()
            time.sleep(1)  # Run the motor
            turn_off_motor()
            time.sleep(2)  # Wait before turning on again
    except KeyboardInterrupt:
        # Clean up GPIO on keyboard interrupt
        GPIO.cleanup()
        print("\nGPIO cleaned up. Exiting.")