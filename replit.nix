{ pkgs }: {
  deps = [
    pkgs.python311
    pkgs.python311Packages.pip
    pkgs.python311Packages.pytelegrambotapi
    pkgs.python311Packages.flask
  ];
}
