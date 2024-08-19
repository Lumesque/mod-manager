{
  description = "A very basic flake";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-24.05";
  };

  outputs = { self, nixpkgs , ...}: 
  let
    system = "x86_64-linux";
    pkgs = import nixpkgs {inherit system;};
    app = pkgs.python312Packages.buildPythonApplication {
      name = "mod-manager";
      pname = "mod-manager";
      format = "pyproject";
      src = ./.;
      nativeBuildInputs = [
        (pkgs.python312.withPackages (pp: [
          pp.hatchling
          pp.hatch-vcs
        ]))
      ];
      propagatedBuildInputs = [
        (pkgs.python312.withPackages (pp: [
          pp.click
          pp.requests
        ]))
      ];
    };
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
            pp.hatchling
            pp.hatch-vcs
            pp.pytest
          ]))
          pkgs.ruff
          (pkgs.hatch.overrideAttrs (prev: {
            disabledTests = prev.disabledTests ++ [
              "test_field_readme"
              "test_field_string"
              "test_field_complex"
              "test_plugin_dependencies_unmet"
            ];
          }))
          #unpkgs.hatch
        ];
      };
      py10 = pkgs.mkShell {
        packages = [
          (pkgs.python39.withPackages (pp: [
            pp.requests
            pp.click
          ]))
          (pkgs.hatch.overrideAttrs (prev: {
            disabledTests = prev.disabledTests ++ [
              "test_field_readme"
              "test_field_string"
              "test_field_complex"
              "test_plugin_dependencies_unmet"
            ];
          }))
        ];
      };

      dev-build = pkgs.mkShell {
        packages = [
          (pkgs.python312.withPackages (pp: [
            pp.hatchling
            pp.hatch-vcs
            pp.pytest
          ]))
          app
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
          pp.hatchling
          pp.hatch-vcs
          pp.pytest
        ]))
        pkgs.ruff
        (pkgs.hatch.overrideAttrs (prev: {
          disabledTests = prev.disabledTests ++ [
            "test_field_readme"
            "test_field_string"
            "test_field_complex"
            "test_plugin_dependencies_unmet"
          ];
        }))
      ];
    };
  };
}
