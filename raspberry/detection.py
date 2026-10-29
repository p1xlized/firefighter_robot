"""Camera capture and fire detection for the Raspberry Pi."""

import shutil
import subprocess
import time
from collections.abc import Iterator
from typing import Protocol

import cv2
import numpy as np

from raspberry.pump import turn_off_pump_motor

MIN_FIRE_AREA = 800
FOUND_AREA_RATIO = 0.20
CENTER_TOLERANCE_RATIO = 0.10
SCAN_SECONDS = 0.8
SEARCH_TURN_SECONDS = 1.2
PUBLISH_RETRY_SECONDS = 2.0
LOWER_FIRE = np.array([18, 50, 50], dtype=np.uint8)
UPPER_FIRE = np.array([35, 255, 255], dtype=np.uint8)


class RobotController(Protocol):
    def move(self, command: str) -> None: ...

    def read_serial(self) -> list[str]: ...


class MediaMtxPublisher:
    """Publish annotated OpenCV frames to MediaMTX through RTSP."""

    def __init__(self, path: str = "fire", width: int = 640, height: int = 480) -> None:
        self.server = None
        self.publisher = None
        self.path = path
        self.last_retry = 0.0
        self.width = width
        self.height = height
        if not shutil.which("mediamtx") or not shutil.which("ffmpeg"):
            print("MediaMTX disabled: mediamtx or ffmpeg is not installed.")
            return

        self.server = subprocess.Popen(
            ["mediamtx"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        time.sleep(1.0)
        self._start_publisher()
        print(f"MediaMTX WebRTC stream: http://<raspberry-pi-ip>:8889/{path}")

    def _start_publisher(self) -> None:
        if self.publisher is not None:
            return
        self.publisher = subprocess.Popen(
            [
                "ffmpeg", "-loglevel", "error",
                "-f", "rawvideo", "-pix_fmt", "bgr24",
                "-video_size", f"{self.width}x{self.height}", "-framerate", "15",
                "-i", "-", "-an", "-c:v", "libx264", "-preset", "ultrafast",
                "-tune", "zerolatency", "-pix_fmt", "yuv420p",
                "-f", "rtsp", "-rtsp_transport", "tcp",
                f"rtsp://127.0.0.1:8554/{self.path}",
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def publish(self, frame: np.ndarray) -> None:
        if self.server is None or self.server.poll() is not None:
            return
        if self.publisher is None or self.publisher.poll() is not None:
            now = time.monotonic()
            if now - self.last_retry < PUBLISH_RETRY_SECONDS:
                return
            self.last_retry = now
            if self.publisher is not None:
                self.publisher.wait()
                self.publisher = None
            self._start_publisher()
        if self.publisher.stdin is None:
            return
        frame = cv2.resize(frame, (self.width, self.height))
        try:
            self.publisher.stdin.write(frame.tobytes())
        except (BrokenPipeError, OSError):
            self._stop_publisher()

    def _stop_publisher(self) -> None:
        if self.publisher is None:
            return
        if self.publisher.stdin:
            self.publisher.stdin.close()
        if self.publisher.poll() is None:
            self.publisher.terminate()
        self.publisher.wait(timeout=3)
        self.publisher = None

    def close(self) -> None:
        if self.publisher:
            self._stop_publisher()
        if self.server:
            self.server.terminate()
            self.server.wait(timeout=3)
            self.server = None


def rpicam_frames(command: str) -> Iterator[np.ndarray]:
    process = subprocess.Popen(
        [
            command, "--timeout", "0", "--nopreview", "--codec", "mjpeg",
            "--inline", "--width", "640", "--height", "480",
            "--framerate", "15", "--quality", "80", "--output", "-",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    try:
        data = b""
        assert process.stdout is not None
        while process.poll() is None:
            chunk = process.stdout.read(4096)
            if not chunk:
                break
            data += chunk
            while b"\xff\xd8" in data and b"\xff\xd9" in data:
                start = data.index(b"\xff\xd8")
                end = data.index(b"\xff\xd9", start) + 2
                frame = cv2.imdecode(
                    np.frombuffer(data[start:end], dtype=np.uint8),
                    cv2.IMREAD_COLOR,
                )
                data = data[end:]
                if frame is not None:
                    yield frame
    finally:
        process.terminate()
        process.wait(timeout=3)


def usb_frames(source: int) -> Iterator[np.ndarray]:
    capture = cv2.VideoCapture(source, cv2.CAP_V4L2)
    if not capture.isOpened():
        raise RuntimeError(f"Unable to open USB camera /dev/video{source}")
    try:
        while True:
            success, frame = capture.read()
            if success:
                yield frame
    finally:
        capture.release()


def analyze_fire(frame: np.ndarray) -> tuple[np.ndarray, tuple[int, int] | None, float]:
    """Return the fire mask, target center, and largest target area."""
    blurred = cv2.GaussianBlur(frame, (21, 21), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, LOWER_FIRE, UPPER_FIRE)
    contours, _ = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    target = max(contours, key=cv2.contourArea, default=None)
    if target is None:
        return mask, None, 0

    area = cv2.contourArea(target)
    moments = cv2.moments(target)
    if area < MIN_FIRE_AREA or moments["m00"] == 0:
        return mask, None, area

    center = (
        int(moments["m10"] / moments["m00"]),
        int(moments["m01"] / moments["m00"]),
    )
    return mask, center, area


def scan_for_fire(robot: RobotController, frames: Iterator[np.ndarray]) -> str:
    """Turn both ways briefly and choose the side with the strongest target."""
    scores: dict[str, float] = {}
    for direction in ("L", "R"):
        robot.move(direction)
        deadline = time.monotonic() + SCAN_SECONDS
        score = 0.0
        while time.monotonic() < deadline:
            try:
                frame = next(frames)
            except StopIteration:
                break
            _, _, area = analyze_fire(frame)
            score = max(score, area)
        robot.move("S")
        scores[direction] = score

    direction = max(scores, key=lambda candidate: scores[candidate])
    print(f"Obstacle avoidance: turning {direction} (fire scores: {scores})")
    robot.move(direction)
    time.sleep(SCAN_SECONDS)
    robot.move("S")
    return direction


def detect_fire(
    robot: RobotController,
    source: int,
    display: bool = False,
    stream: bool = True,
) -> None:
    camera_command = shutil.which("rpicam-vid") or shutil.which("libcamera-vid")
    frames = rpicam_frames(camera_command) if camera_command else usb_frames(source)
    print("Fire detection started. Press Ctrl+C to stop.")
    last_command = None
    found = False
    search_direction = "L"
    search_started = time.monotonic()
    publisher = MediaMtxPublisher() if stream else None

    try:
        for frame in frames:
            if any(
                "Obstacle encountered while moving! Emergency stop." in message
                for message in robot.read_serial()
            ):
                print("Obstacle detected. Scanning for the best route.")
                scan_for_fire(robot, frames)
                last_command = "S"
                search_started = time.monotonic()
                continue

            height, width = frame.shape[:2]
            mask, center, area = analyze_fire(frame)
            command = "S"
            status = "Searching"

            if center is not None:
                center_x = center[0]
                offset = center_x - width // 2
                centered = abs(offset) <= width * CENTER_TOLERANCE_RATIO
                close_enough = area >= width * height * FOUND_AREA_RATIO

                if close_enough and centered:
                    command = "S"
                    status = "FOUND"
                    if not found:
                        print("FOUND: fire is in front of the robot.")
                        turn_off_pump_motor()
                        found = True
                        time.sleep(10.0)
                        turn_off_pump_motor()
                        found = False

                elif offset < 0:
                    command = "L"
                    status = "Aligning left"
                    found = False
                elif offset > 0:
                    command = "R"
                    status = "Aligning right"
                    found = False
                else:
                    command = "F"
                    status = "Driving forward"
                    found = False
            else:
                found = False
                if time.monotonic() - search_started >= SEARCH_TURN_SECONDS:
                    search_direction = "R" if search_direction == "L" else "L"
                    search_started = time.monotonic()
                command = search_direction
                status = f"Searching ({search_direction})"

            if command != last_command:
                robot.move(command)
                last_command = command

            preview = cv2.bitwise_and(frame, frame, mask=mask)
            if center is not None:
                cv2.circle(preview, center, 8, (255, 255, 255), -1)
            cv2.putText(
                preview, status, (20, 35), cv2.FONT_HERSHEY_SIMPLEX,
                1, (255, 255, 255), 2,
            )
            if publisher:
                publisher.publish(preview)
            if display:
                cv2.imshow("Fire detection", preview)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
    finally:
        if publisher:
            publisher.close()
        if display:
            cv2.destroyAllWindows()


def camera_test(source: int, display: bool = False) -> None:
    """Capture the camera and publish it without requiring an Arduino."""
    camera_command = shutil.which("rpicam-vid") or shutil.which("libcamera-vid")
    frames = rpicam_frames(camera_command) if camera_command else usb_frames(source)
    publisher = MediaMtxPublisher(path="camera")
    print("Camera test started.")
    print("MediaMTX WebRTC stream: http://<raspberry-pi-ip>:8889/camera")

    try:
        for frame in frames:
            publisher.publish(frame)
            if display:
                cv2.imshow("Camera test", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
    finally:
        publisher.close()
        if display:
            cv2.destroyAllWindows()
