"""Application entry point."""
import argparse
import time
import serial

def main() -> None:
    parser = argparse.ArgumentParser(description="Fire detection robot - Movement Test")
    parser.add_argument(
        "--arduino-port",
        default="/dev/ttyACM0",
        help="Serial port, for example /dev/ttyACM0 or /dev/ttyUSB0"
    )
    args = parser.parse_args()

    # Open the serial port (triggers Arduino reset)
    ser = serial.Serial(args.arduino_port, 9600, timeout=1)
    ser.write_timeout = 1

    # Give the Arduino time to finish rebooting (increase to 2.0 if commands are missed)
    print("Waiting for Arduino to boot...")
    time.sleep(2.0)

    # List of movement commands to test sequentially
    commands = [
        (b'B\n', "Backwards"),
        (b'F\n', "Forwards"),
        (b'L\n', "Left"),
        (b'R\n', "Right"),
        (b'S\n', "Stop")
    ]

    for cmd, name in commands:
        print(f"Sending {name} ({cmd.decode().strip()})...")
        ser.write(cmd)
        ser.flush()

        # Short pause for the Arduino to execute the movement
        time.sleep(0.5)

        # Read response if the Arduino sends one back
        if ser.in_waiting > 0:
            response = ser.readline().decode().strip()
            print(f"  -> Response: {response}")

    ser.close()
    print("Movement test complete.")

if __name__ == "__main__":
    main()
