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

The Raspberry Pi camera is published to MediaMTX as `fire`. The WebRTC stream is available at:

```text
http://<raspberry-pi-ip>:8889/fire
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
