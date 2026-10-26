"""Application entry point."""
import argparse
import time
import serial

def main() -> None:
    parser = argparse.ArgumentParser(description="Fire detection robot")
    parser.add_argument(
        "--arduino-port",
        default="/dev/ttyACM0",
        help="Serial port, for example /dev/ttyACM0 or /dev/ttyUSB0"
    )
    args = parser.parse_args()

    # Open the serial port (this triggers an Arduino reboot)
    ser = serial.Serial(args.arduino_port, 9600, timeout=1)
    ser.write_timeout = 1

    # CRITICAL: Wait 2 seconds for the Arduino to finish rebooting and booting up
    time.sleep(0.5)

    # Now send the commands safely
    ser.write(b'B\n')
    time.sleep(0.5)  # Wait for Arduino to process the command
    ser.write(b'F\n')
    time.sleep(0.5)  # Wait for Arduino to process the command
    ser.write(b'L\n')
    time.sleep(0.5)  # Wait for Arduino to process the command
    ser.write(b'R\n')
    time.sleep(0.5)  # Wait for Arduino to process the command
    ser.write(b'S\n')
    ser.flush()

    # Read the response from Arduino
    response = ser.readline().decode().strip()
    print(f"Received: {response}")

    ser.close()

if __name__ == "__main__":
    main()
