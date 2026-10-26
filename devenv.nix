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

  languages.python = {
      enable = true;
      venv = {
        enable = true;
        requirements = ./requirements.txt;
      };
    };

    javascript = {
      enable = true;
      nodejs.enable = true;
    };


  # Hook that runs automatically when you enter `devenv shell`


    # Automatically create a symbolic link from .venv in your project root
    # to devenv's internal state directory for seamless IDE and tool integration
    enterShell = ''
      if [ -d "$DEVENV_STATE/venv" ]; then
        ln -sfn "$DEVENV_STATE/venv" .venv
        echo "Linked .venv -> $DEVENV_State/venv"
      fi
    '';
}
