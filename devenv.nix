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

  languages.python = {
    enable = true;
    venv = {
      enable = true;
      requirements = ./requirements.txt;
    };
  };

  languages.javascript = {
    enable = true;
    nodejs.enable = true;
  };

  # Hook that runs automatically when you enter `devenv shell`
  enterShell = ''
    if [ -d "$DEVENV_STATE/venv" ]; then
      ln -sfn "$DEVENV_STATE/venv" .venv
      echo "Linked .venv -> $DEVENV_STATE/venv"
    fi
  '';
}
