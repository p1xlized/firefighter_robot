"""Headless fire detection and Arduino movement control for Raspberry Pi."""

import argparse
import select
import sys
import time
import termios
import tty

import serial

try:
    from .detection import camera_test, detect_fire
    from .pump import test_pump, turn_off_pump_motor, turn_on_pump_motor
except ImportError:
    from detection import camera_test, detect_fire
    from pump import test_pump, turn_off_pump_motor, turn_on_pump_motor

CAMERA_SOURCE = 0
ARDUINO_PORT = "/dev/ttyACM0"
BAUD_RATE = 9600


class Robot:
    def __init__(self, port: str) -> None:
        self.serial = serial.Serial(port, BAUD_RATE, timeout=1, write_timeout=1)
        self._speed_command: str | None = None
        time.sleep(2)

    def move(self, command: str) -> None:
        if command not in {"F", "B", "L", "R", "S", "V", "1", "2", "3"}:
            raise ValueError("Command must be F, B, L, R, S, V, 1, 2, or 3")
        if command in {"1", "2", "3"}:
            if command == self._speed_command:
                return
            self._speed_command = command
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


def manual_control(
    port: str,
    camera_source: int,
    stream: bool,
    speed: int = 2,
) -> None:
    """Control the robot with WASD from a TTY."""
    if not sys.stdin.isatty():
        raise RuntimeError("Manual control requires an interactive TTY")

    robot = Robot(port)
    previous_terminal = termios.tcgetattr(sys.stdin)
    commands = {"w": "F", "a": "L", "s": "B", "d": "R", " ": "S"}
    pump_active = False
    try:
        tty.setcbreak(sys.stdin.fileno())
        robot.move(str(speed))
        print(
            "Manual control: W/A/S/D move, space stops, P pump, V buzzer, "
            "Q detects fire, X quits."
        )
        while True:
            ready, _, _ = select.select([sys.stdin], [], [], 0.1)
            if not ready:
                continue
            key = sys.stdin.read(1).lower()
            if key == "x":
                break
            if key == "q":
                print("Starting autonomous fire detection. Press Ctrl+C to stop.")
                detect_fire(robot, camera_source, stream=stream)
                print("Fire detection stopped. Returning to manual control.")
                continue
            if key == "p":
                pump_active = not pump_active
                if pump_active:
                    turn_on_pump_motor()
                    print("Pump ON")
                else:
                    turn_off_pump_motor()
                    print("Pump OFF")
                continue
            if key == "v":
                robot.move("V")
                print("Buzzer command sent")
                continue
            if key in {"1", "2", "3"}:
                robot.move(key)
                print(f"Speed level {key}")
            elif key in commands:
                robot.move(commands[key])
    finally:
        if pump_active:
            turn_off_pump_motor()
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, previous_terminal)
        robot.close()
    print("Manual control stopped.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--test", action="store_true", help="Run the Arduino movement test")
    parser.add_argument(
        "--manual",
        action="store_true",
        help="Control the robot interactively with WASD",
    )
    parser.add_argument(
        "--move",
        choices=("F", "B", "L", "R", "S", "V", "1", "2", "3"),
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
    if args.manual:
        manual_control(
            args.arduino_port,
            args.camera_source,
            stream=not args.no_stream,
        )
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
