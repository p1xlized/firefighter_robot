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
  ] ++ lib.optionals (!pkgs.stdenv.hostPlatform.isAarch64) [
    pkgs.arduino-ide
  ];

  languages = {
    python = {
      enable = true;
      venv = {
        enable = true;
        requirements = ./raspberry/requirement.txt; # Correct location for requirements.txt
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
