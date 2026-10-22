from contextlib import asynccontextmanager
import cv2
import serial
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# Global variables for hardware resources
ser = None
camera = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global ser, camera

    # --- STARTUP: Initialize Serial and Camera ---
    try:
        ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
        ser.write_timeout = 1
        print("Serial port /dev/ttyUSB0 opened successfully.")
    except Exception as e:
        print(f"Warning: Could not open serial port: {e}")
        ser = None

    camera = cv2.VideoCapture(0)
    print("Camera initialized.")

    yield  # Server is running and handling requests...

    # --- SHUTDOWN: Clean up resources ---
    if ser and ser.is_open:
        ser.close()
        print("Serial port closed.")
    if camera and camera.isOpened():
        camera.release()
        print("Camera released.")

app = FastAPI(lifespan=lifespan)

# Pydantic model for receiving commands via API
class RobotCommand(BaseModel):
    command: str  # e.g., "F", "B", etc.

def generate_frames():
    while camera and camera.isOpened():
        success, frame = camera.read()
        if not success:
            break
        else:
            # TODO: Add your OpenCV fire detection logic here!

            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()

            # Yield frame for MJPEG stream
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.get("/video_feed")
async def video_feed():
    return StreamingResponse(generate_frames(),
                             media_type="multipart/x-mixed-replace; boundary=frame")

@app.post("/robot/control")
async def control_robot(payload: RobotCommand):
    """Send commands to the Arduino via API (e.g., manual override)"""
    if not ser or not ser.is_open:
        return {"status": "error", "message": "Serial port is not connected."}

    try:
        # Format command with a newline similar to your script
        command_bytes = (payload.command.strip() + "\n").encode('utf-8')
        ser.write(command_bytes)
        ser.flush()

        # Read optional response back from Arduino
        response = ser.readline().decode().strip()
        return {
            "status": "success",
            "sent": payload.command,
            "arduino_response": response
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/")
def index():
    return {"message": "Robot Stream & Control Server is active!"}
