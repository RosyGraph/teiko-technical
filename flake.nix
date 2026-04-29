{
  description = "Python dev shell";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
  };

  outputs = {
    self,
    nixpkgs,
  }: let
    forAllSystems = nixpkgs.lib.genAttrs [
      "x86_64-linux"
      "aarch64-linux"
      "x86_64-darwin"
      "aarch64-darwin"
    ];
  in {
    devShells = forAllSystems (system: let
      pkgs = import nixpkgs {inherit system;};

      linuxRuntimeLibs = with pkgs; [
        stdenv.cc.cc.lib # libstdc++.so.6
        zlib
        glib
      ];
    in {
      default = pkgs.mkShell {
        packages = with pkgs;
          [
            python312
            uv
            ruff
            ty
          ]
          ++ nixpkgs.lib.optionals pkgs.stdenv.isLinux linuxRuntimeLibs;

        shellHook = nixpkgs.lib.optionalString pkgs.stdenv.isLinux ''
          export LD_LIBRARY_PATH=${pkgs.lib.makeLibraryPath linuxRuntimeLibs}:$LD_LIBRARY_PATH
        '';
      };
    });
  };
}
