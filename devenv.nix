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
    pkgs.opencv
  ] ++ lib.optionals (!pkgs.stdenv.hostPlatform.isAarch64) [
    pkgs.arduino-ide
  ];

  languages = {
    python = {
      enable = true;
      uv = {
        enable = true;
        requirements = "raspberry/requirement.txt";
      };
      venv.enable = true;
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
