{
  pkgs,
  lib,
  config,
  ...
}:
{
  packages = [
    pkgs.arduino-cli
    pkgs.zlib
    pkgs.libxcb
    pkgs.libGL
    pkgs.glib
    pkgs.libcamera
    pkgs.python314Packages.numpy
    pkgs.python314Packages.opencv4
    pkgs.python314Packages.pyserial
    pkgs.python314Packages.fastapi
    pkgs.python314Packages.uvicorn
  ] ++ lib.optionals (!pkgs.stdenv.hostPlatform.isAarch64) [
    pkgs.arduino-ide
  ];

  languages = {
    python = {
      enable = true;
      venv = {
        enable = true;
        requirements = ./raspberry/requirements.txt; # Correct location for requirements.txt
      };
    };
    javascript = {
      enable = true;
      nodejs.enable = true;
    };
  };

  enterShell = ''
    export PATH="$PATH:/usr/bin:/usr/sbin"
  '';
}
