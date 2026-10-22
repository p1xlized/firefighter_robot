"""Application entry point."""
import serial



# def main() -> None:
#     parser = argparse.ArgumentParser(description="Fire detection robot")
#     parser.add_argument("--source", default="0", help="Camera index or video file path")
#     parser.add_argument("--arduino-port", help="Serial port, for example /dev/ttyACM0")
#     parser.add_argument("--alarm", default="alarm-sound.mp3", help="Alarm audio file")
#     args = parser.parse_args()
#
#     robot = RobotController(args.arduino_port)
#     detect_fire(args.source, robot, Path(args.alarm))
def main() -> None:
    ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
    ser.write(b'B\n')
    ser.write_timeout = 1
    ser.write(b'F\n')
    ser.timeout = 1
    ser.flush()
    print(ser.readline().decode().strip())
    ser.close()

if __name__ == "__main__":
    main()
