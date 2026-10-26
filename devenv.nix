{
  pkgs,
  lib,
  config,
  ...
}:
{
  packages = [
    pkgs.arduino-cli
    pkgs.opencv
    pkgs.zlib
    pkgs.libxcb
    pkgs.libGL
    pkgs.glib
    pkgs.python314Packages.pyserial
    pkgs.python314Packages.numpy
    pkgs.python314Packages.opencv4
  ] ++ lib.optionals (!pkgs.stdenv.hostPlatform.isAarch64) [
    pkgs.arduino-ide
  ];

  languages = {
    python = {
      enable = true;
      # Disable default auto-venv so we can manage it with system-site-packages
      venv.enable = false;
    };
    javascript = {
      enable = true;
      nodejs.enable = true;
    };
  };

  # Hook that runs automatically when you enter `devenv shell`
  enterShell = ''
    # Export system paths so libcamera and other Raspberry Pi binaries work
    export PATH="$PATH:/usr/bin:/usr/sbin"

    # Create a local virtual environment with system site-packages enabled (links to apt-installed picamera2)
    if [ ! -d ".venv" ]; then
      python3 -m venv --system-site-packages .venv
    fi

    # Activate the virtual environment automatically
    source .venv/bin/activate
  '';
}
