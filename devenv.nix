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
  ];

  languages = {
    python = {
      enable = true;
      uv.enable = true;
      venv.enable = true;
    };
  };
}
