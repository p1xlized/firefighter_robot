from gpiozero import DigitalOutputDevice
from time import sleep

# Initialize the relay on GPIO 22
# active_high=False accounts for active-LOW relay modules (clicks on LOW signal)
pump = DigitalOutputDevice(2, active_high=False)

print("Starting water pump for 5 seconds...")
pump.on()   # Turns the relay on -> pump runs
sleep(5)

print("Stopping water pump.")
pump.off()  # Turns the relay off -> pump stops
