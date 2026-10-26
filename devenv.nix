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
    pkgs.libcamera
    pkgs.python314Packages.pyserial
    pkgs.python314Packages.numpy
    pkgs.python314Packages.opencv4
  ] ++ lib.optionals (!pkgs.stdenv.hostPlatform.isAarch64) [
    pkgs.arduino-ide
  ];

  languages = {
    python = {
      enable = true;
      uv.enable = true;
      venv.enable = true;
    };
    javascript = {
      enable = true;
      nodejs.enable = true;
    };
  };
}
