"""Raspberry Pi camera stream and robot API."""
import argparse
import time
from contextlib import asynccontextmanager
from threading import Lock

import cv2
import serial
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel

CAMERA_SOURCE = 0
ARDUINO_PORT = "/dev/ttyACM0"
BAUD_RATE = 9600
ALLOWED_COMMANDS = {"F", "B", "L", "R", "S"}

camera: cv2.VideoCapture | None = None
arduino: serial.Serial | None = None
camera_lock = Lock()


class RobotCommand(BaseModel):
    command: str


@asynccontextmanager
async def lifespan(_: FastAPI):
    global camera, arduino

    camera = cv2.VideoCapture(CAMERA_SOURCE, cv2.CAP_V4L2)
    if not camera.isOpened():
        camera.release()
        camera = None
        print(f"Warning: unable to open camera /dev/video{CAMERA_SOURCE}")
    else:
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    try:
        arduino = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=1, write_timeout=1)
        print(f"Arduino connected on {ARDUINO_PORT}")
    except serial.SerialException as error:
        print(f"Warning: Arduino unavailable: {error}")

    yield

    if arduino and arduino.is_open:
        arduino.write(b"S\n")
        arduino.close()
    if camera:
        camera.release()


app = FastAPI(title="Firefighter Robot", lifespan=lifespan)


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


def generate_frames():
    if camera is None:
        return
    while camera.isOpened():
        with camera_lock:
            success, frame = camera.read()
        if not success:
            continue
        encoded, buffer = cv2.imencode(".jpg", frame)
        if encoded:
            yield (
                b"--frame\r\nContent-Type: image/jpeg\r\n\r\n"
                + buffer.tobytes()
                + b"\r\n"
            )


@app.get("/", response_class=HTMLResponse)
def health():
    return """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Firefighter Robot Camera</title>
    <style>
      body { margin: 0; padding: 2rem; background: #111; color: #fff;
             font: 1rem system-ui, sans-serif; text-align: center; }
      img { display: block; width: min(100%, 960px); margin: 1rem auto;
            border: 2px solid #444; border-radius: 8px; }
    </style>
  </head>
  <body>
    <h1>Firefighter Robot Camera</h1>
    <img src="/video_feed" alt="Live camera feed">
  </body>
</html>"""


@app.get("/video_feed")
def video_feed():
    if camera is None:
        raise HTTPException(status_code=503, detail="Camera is unavailable")
    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


@app.post("/robot/control")
def control_robot(payload: RobotCommand):
    command = payload.command.strip().upper()
    if command not in ALLOWED_COMMANDS:
        raise HTTPException(status_code=400, detail="Command must be F, B, L, R, or S")
    if arduino is None or not arduino.is_open:
        raise HTTPException(status_code=503, detail="Arduino is unavailable")
    try:
        arduino.write(f"{command}\n".encode("ascii"))
        arduino.flush()
    except serial.SerialException as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    return {"status": "success", "sent": command}


def main() -> None:
    global ARDUINO_PORT

    parser = argparse.ArgumentParser(description="Firefighter robot camera API")
    parser.add_argument("--test", action="store_true", help="Run the Arduino movement test and exit")
    parser.add_argument(
        "--arduino-port",
        default=ARDUINO_PORT,
        help="Serial port, for example /dev/ttyACM0 or /dev/ttyUSB0",
    )
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    ARDUINO_PORT = args.arduino_port
    if args.test:
        movement_test(args.arduino_port)
    else:
        uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
