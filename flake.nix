{
  description = "A very basic flake";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-24.05";
  };

  outputs = { self, nixpkgs }: 
  let
    system = "x86_64-linux";
    pkgs = import nixpkgs {inherit system;};
  in
  {
    devShells.${system} = {
      default = pkgs.mkShell {
        packages = [
          (pkgs.python312.withPackages (pp: [
            pp.ipython
            pp.requests
            pp.click
            pp.twine
          ]))
          pkgs.ruff
        ];
      };
      py10 = pkgs.mkShell {
        packages = [
          (pkgs.python39.withPackages (pp: [
#            pp.ipython
            pp.requests
            pp.click
          ]))
        ];
      };
    };
    packages.${system}.default = pkgs.symlinkJoin {
      name = "nix shell developer env";
      paths = [
        (pkgs.python312.withPackages (pp: [
          pp.ipython
          pp.requests
          pp.click
          pp.twine
        ]))
        pkgs.ruff
      ];
    };
  };
}
