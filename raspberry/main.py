"""Headless fire detection and Arduino movement control for Raspberry Pi."""

import argparse
import time

import serial

try:
    from .detection import camera_test, detect_fire
    from .pump import test_pump
except ImportError:
    from detection import camera_test, detect_fire
    from pump import test_pump

CAMERA_SOURCE = 0
ARDUINO_PORT = "/dev/ttyACM0"
BAUD_RATE = 9600


class Robot:
    def __init__(self, port: str) -> None:
        self.serial = serial.Serial(port, BAUD_RATE, timeout=1, write_timeout=1)
        time.sleep(2)

    def move(self, command: str) -> None:
        if command not in {"F", "B", "L", "R", "S", "1", "2", "3"}:
            raise ValueError("Command must be F, B, L, R, S, 1, 2, or 3")
        self.serial.write(f"{command}\n".encode("ascii"))
        self.serial.flush()

    def drive(self, command: str, speed: int = 2) -> None:
        """Set speed and movement together so every correction keeps moving."""
        self.move(str(speed))
        self.move(command)

    def read_serial(self) -> list[str]:
        messages = []
        while self.serial.in_waiting:
            message = self.serial.readline().decode("utf-8", errors="replace").strip()
            if message:
                messages.append(message)
                print(f"Arduino: {message}")
        return messages

    def close(self) -> None:
        if self.serial.is_open:
            self.move("S")
            self.serial.close()

    def autonomous_drive(self, camera_source: int, display: bool) -> None:
        detect_fire(self, camera_source, display)

def movement_test(port: str) -> None:
    robot = Robot(port)
    try:
        for command, name in (
            ("B", "Backwards"),
            ("F", "Forwards"),
            ("L", "Left"),
            ("R", "Right"),
            ("S", "Stop"),
        ):
            print(f"Sending {name} ({command})")
            robot.move(command)
            time.sleep(0.5)
    finally:
        robot.close()
    print("Movement test complete.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--test", action="store_true", help="Run the Arduino movement test")
    parser.add_argument(
        "--move",
        choices=("F", "B", "L", "R", "S", "1", "2", "3"),
        help="Send one movement or speed command",
    )
    parser.add_argument("--test-pump", action="store_true", help="Run the pump test")
    parser.add_argument(
        "--camera-test",
        action="store_true",
        help="Test the camera and stream it through MediaMTX without Arduino",
    )
    parser.add_argument("--arduino-port", default=ARDUINO_PORT)
    parser.add_argument("--camera-source", type=int, default=CAMERA_SOURCE)
    parser.add_argument("--display", action="store_true", help="Show a preview when a desktop is available")
    parser.add_argument("--no-stream", action="store_true", help="Disable the MediaMTX camera stream")
    args = parser.parse_args()

    if args.test:
        movement_test(args.arduino_port)
        return
    if args.test_pump:
        test_pump()
        return
    if args.camera_test:
        camera_test(args.camera_source, args.display)
        return

    robot = Robot(args.arduino_port)
    try:
        if args.move:
            robot.move(args.move)
        else:
            print("Starting fire detection...")
            detect_fire(
                robot,
                args.camera_source,
                args.display,
                stream=not args.no_stream,
            )
    except KeyboardInterrupt:
        print("\nStopping.")
    finally:
        robot.close()


if __name__ == "__main__":
    main()
