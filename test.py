"""Application entry point."""
import argparse
import serial

def main() -> None:
    parser = argparse.ArgumentParser(description="Fire detection robot")
    parser.add_argument(
        "--arduino-port",
        default="/dev/ttyACM0",
        help="Serial port, for example /dev/ttyACM0 or /dev/ttyUSB0"
    )
    args = parser.parse_args()

    # Use the path provided via command-line argument
    ser = serial.Serial(args.arduino_port, 9600, timeout=1)
    ser.write_timeout = 1

    ser.write(b'B\n')
    ser.write(b'F\n')
    ser.flush()

    print(ser.readline().decode().strip())
    ser.close()

if __name__ == "__main__":
    main()
