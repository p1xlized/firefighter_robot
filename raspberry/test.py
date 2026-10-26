"""Application entry point."""
import argparse
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


def camera_test(source: int, use_picamera: bool) -> None:
    """Preview a CSI camera through Picamera2 or a USB camera through OpenCV."""
    picamera = None
    capture = None

    if use_picamera:
        try:
            from picamera2 import Picamera2
        except ImportError as error:
            raise RuntimeError(
                "Picamera2 is not installed. Run: sudo apt install -y python3-picamera2"
            ) from error

        picamera = Picamera2()
        picamera.configure(picamera.create_preview_configuration(main={"format": "BGR888"}))
        picamera.start()
    else:
        capture = cv2.VideoCapture(source, cv2.CAP_V4L2)
        if not capture.isOpened():
            raise RuntimeError(f"Unable to open camera /dev/video{source}")
        capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    print("Camera preview started. Press q to quit.")
    try:
        while True:
            frame = picamera.capture_array() if picamera else capture.read()[1]
            if frame is None:
                print("Camera returned no frame.")
                break

            cv2.imshow("Raspberry Pi camera", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        if picamera:
            picamera.stop()
            picamera.close()
        if capture:
            capture.release()
        cv2.destroyAllWindows()


def test() -> None:
    parser = argparse.ArgumentParser(description="Fire detection robot - Movement Test")
    parser.add_argument(
        "--arduino-port",
        default="/dev/ttyACM0",
        help="Serial port, for example /dev/ttyACM0 or /dev/ttyUSB0",
    )
    parser.add_argument("--camera", action="store_true", help="Preview the camera")
    parser.add_argument("--camera-source", type=int, default=0, help="USB camera index")
    parser.add_argument(
        "--picamera",
        action="store_true",
        help="Use a Raspberry Pi CSI camera through Picamera2",
    )
    args = parser.parse_args()

    if args.camera:
        camera_test(args.camera_source, args.picamera)
    else:
        movement_test(args.arduino_port)

if __name__ == "__main__":
    test()
