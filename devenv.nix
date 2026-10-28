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
          # Use withPackages to bundle system-level hardware libraries like gpiozero
          package = pkgs.python314.withPackages (ps: [
            ps.gpiozero
            ps.rpi-lgpio
            ps.numpy
            ps.opencv4
            ps.pyserial
            ps.fastapi
            ps.uvicorn
          ]);
          venv = {
            enable = true;
            requirements = ./raspberry/requirements.txt;
          };
        };
javascript.enable = true;
javascript.pnpm.enable = true;


  };

  enterShell = ''
    export PATH="$PATH:/usr/bin:/usr/sbin"
  '';
}
