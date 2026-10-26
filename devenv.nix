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
      uv = {
        enable = true;
        requirements = "raspberry/requirement.txt"; # Pointing to the correct subfolder
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
