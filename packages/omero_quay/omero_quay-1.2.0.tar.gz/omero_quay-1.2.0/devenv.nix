{pkgs, ...}: {
  packages = with pkgs; [
    conda
    hatch
    python312Packages.hatchling
  ];

  enterShell = ''
    conda-shell
    conda-install -u
    conda env update --file environment.yml
  '';
}
