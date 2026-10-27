"""Application entry point."""
import argparse
import os
import time

import cv2
import serial


def movement_test(port: str) -> None:
    """Verify that the Arduino receives all movement commands."""
    ser = serial.Serial(port, 9600, timeout=1, write_timeout=1)
    print("Waiting for Arduino to boot...")
    time.sleep(2.0)

    commands = [
        (b"B\n", "Backwards"),
        (b"F\n", "Forwards"),
        (b"L\n", "Left"),
        (b"R\n", "Right"),
        (b"S\n", "Stop"),
    ]
    try:
        for command, name in commands:
            print(f"Sending {name} ({command.decode().strip()})...")
            ser.write(command)
            ser.flush()
            time.sleep(0.5)
    finally:
        ser.write(b"S\n")
        ser.close()
    print("Movement test complete.")


def camera_test(source: int) -> None:
    """Preview the camera using OpenCV V4L2 (compatible with Pi camera via libcamera wrapper)."""
    capture = cv2.VideoCapture(source, cv2.CAP_V4L2)
    if not capture.isOpened():
        raise RuntimeError(f"Unable to open camera /dev/video{source}")

    capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    has_display = os.environ.get("DISPLAY") is not None
    if not has_display:
        print("WARNING: No graphical display (DISPLAY environment variable) detected.")
        print("cv2.imshow will be disabled. Running in headless mode.")

    print("Camera preview started. Press 'q' in the window to quit (or Ctrl+C in terminal).")
    try:
        while True:
            ret, frame = capture.read()
            if not ret or frame is None:
                print("Camera returned no frame.")
                break

            if has_display:
                cv2.imshow("Raspberry Pi camera", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
            else:
                time.sleep(0.03)

    except KeyboardInterrupt:
        print("\nStopping camera preview...")
    finally:
        capture.release()
        if has_display:
            cv2.destroyAllWindows()


def test() -> None:
    parser = argparse.ArgumentParser(description="Fire detection robot - Movement & Camera Test")
    parser.add_argument(
        "--arduino-port",
        default="/dev/ttyACM0",
        help="Serial port, for example /dev/ttyACM0 or /dev/ttyUSB0",
    )
    parser.add_argument("--camera", action="store_true", help="Preview the camera")
    parser.add_argument("--camera-source", type=int, default=0, help="Camera device index")
    args = parser.parse_args()

    if args.camera:
        camera_test(args.camera_source)
    else:
        movement_test(args.arduino_port)


if __name__ == "__main__":
    test()
