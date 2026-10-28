import RPi.GPIO as GPIO
import time

# Set up GPIO
GPIO.setmode(GPIO.BCM)
relay_pin = 17
GPIO.setup(relay_pin, GPIO.OUT)

# Function to turn on the motor
def turn_on_motor():
    GPIO.output(relay_pin, GPIO.HIGH)
    print("Motor ON")

# Function to turn off the motor
def turn_off_motor():
    GPIO.output(relay_pin, GPIO.LOW)
    print("Motor OFF")

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
