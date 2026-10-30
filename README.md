# Firefighter Robot

Raspberry Pi fire detection and Arduino robot control with OpenCV, MediaMTX, and an Elysia server.

## Raspberry Pi

Enter the development environment:

```bash
devenv shell
```

Run autonomous detection and movement:

```bash
python -m raspberry.main
```

Useful commands:

```bash
python -m raspberry.main --test       # Test Arduino movement
python -m raspberry.main --move F     # Send one movement command
python -m raspberry.main --no-stream  # Disable MediaMTX publishing
```

Fire email notifications are optional. Set these environment variables before
starting the robot to enable them. When fire is detected, Python also sends the
Arduino serial command `V`; configure your Arduino firmware to use that command
for the buzzer.

```bash
export FIRE_SMTP_USERNAME=robot@example.com
export FIRE_SMTP_PASSWORD=your-app-password
export FIRE_ALERT_RECIPIENT=operator@example.com
```

The detector drives forward when no fire target is visible. If the Arduino
reports an obstacle, it slowly scans left and right for up to 15 seconds,
chooses the stronger fire direction, and then resumes forward movement.

The Raspberry Pi camera is always published to MediaMTX as `camera`. The WebRTC stream is available at:

```text
http://<raspberry-pi-ip>:8889/camera
```

## Elysia server

```bash
cd server
pnpm install
pnpm dev
```

Open the static video page at `http://localhost:3000/video-feed`. Set the MediaMTX URL in `server/src/index.ts` to the Raspberry Pi address when the server runs on another machine.

## Development environment

The root `devenv.nix` provides Python, OpenCV, NumPy, PySerial, FFmpeg, MediaMTX, Arduino CLI, and pnpm.
