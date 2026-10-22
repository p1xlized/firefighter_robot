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
    pkgs.arduino-ide
    pkgs.zlib
    pkgs.libxcb
    pkgs.libGL
    pkgs.glib
    pkgs.python314Packages.pyserial
    pkgs.python314Packages.numpy
    pkgs.python314Packages.opencv4
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
