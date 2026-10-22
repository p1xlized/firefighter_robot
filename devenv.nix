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
