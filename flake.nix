{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { nixpkgs, flake-utils, ... }@inputs:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        pip = ps:
          { pname, version, sha256 }:
          ps.pythonPackages.buildPythonPackage {
            inherit pname version;
            src = ps.fetchPypi { inherit pname version sha256; };
            doCheck = false;
          };
      in {
        devShell = pkgs.mkShell {
          packages = [ pkgs.python3 pkgs.python3Packages.pip ];
        };
      });

}
