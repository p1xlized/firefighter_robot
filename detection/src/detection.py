"""Fire detection, alarm, email notification, and Arduino control."""

from __future__ import annotations

import os
import smtplib
import threading
from email.message import EmailMessage
from pathlib import Path

import cv2
import numpy as np
import serial

try:
    from playsound3 import playsound
except ImportError:
    playsound = None


class RobotController:
    def __init__(self, port: str | None, baudrate: int = 9600) -> None:
        self.connection = serial.Serial(port, baudrate, timeout=1) if port else None

    def send(self, command: str) -> None:
        if self.connection and self.connection.is_open:
            self.connection.write(f"{command}\n".encode("ascii"))

    def close(self) -> None:
        if self.connection and self.connection.is_open:
            self.send("S")
            self.connection.close()


def send_mail() -> None:
    sender = os.environ.get("FIRE_EMAIL_SENDER")
    password = os.environ.get("FIRE_EMAIL_PASSWORD")
    recipient = os.environ.get("FIRE_EMAIL_RECIPIENT")
    if not all((sender, password, recipient)):
        print("Email disabled: set FIRE_EMAIL_SENDER, FIRE_EMAIL_PASSWORD, and FIRE_EMAIL_RECIPIENT.")
        return

    message = EmailMessage()
    message["Subject"] = "Fire detected"
    message["From"] = sender
    message["To"] = recipient
    message.set_content("The firefighter robot detected a possible fire.")
    with smtplib.SMTP("smtp.gmail.com", 587, timeout=15) as server:
        server.starttls()
        server.login(sender, password)
        server.send_message(message)


def play_alarm(sound_file: Path) -> None:
    if playsound is None:
        print("Alarm disabled: playsound3 is not installed.")
    elif sound_file.exists():
        playsound(str(sound_file))
    else:
        print(f"Alarm disabled: sound file not found: {sound_file}")


def detect_fire(video_source: str, robot: RobotController, sound_file: Path) -> None:
    source: int | str = int(video_source) if video_source.isdigit() else video_source
    video = cv2.VideoCapture(source)
    if not video.isOpened():
        raise RuntimeError(f"Unable to open video source: {video_source}")

    alerted = False
    try:
        while True:
            grabbed, frame = video.read()
            if not grabbed:
                break

            frame = cv2.resize(frame, (960, 540))
            hsv = cv2.cvtColor(cv2.GaussianBlur(frame, (21, 21), 0), cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(
                hsv,
                np.array([18, 50, 50], dtype=np.uint8),
                np.array([35, 255, 255], dtype=np.uint8),
            )

            if cv2.countNonZero(mask) > 15000 and not alerted:
                alerted = True
                robot.send("S")
                threading.Thread(target=play_alarm, args=(sound_file,), daemon=True).start()
                threading.Thread(target=send_mail, daemon=True).start()

            cv2.imshow("fire detection", cv2.bitwise_and(frame, frame, mask=mask))
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        robot.close()
        video.release()
        cv2.destroyAllWindows()
