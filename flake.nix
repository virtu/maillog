{
  description = "A simple python email logging library.";

  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, flake-utils, poetry2nix }: {
    nixosModules.maillog = import ./module.nix self;
  } // flake-utils.lib.eachDefaultSystem (system:
    let
      # Define a base pkgs without overlays
      pkgs = import nixpkgs { inherit system; };
      # Define overlay for setting custom python version
      inherit (poetry2nix.lib.mkPoetry2Nix { inherit pkgs; }) mkPoetryApplication;
      overlays = [
        (final: prev: {
          maillog = { python }:
            mkPoetryApplication {
              projectDir = ./.;
              inherit python;
            };
        })
      ];
      pkgsWithOverlays = import nixpkgs {
        inherit system;
        overlays = overlays;
      };
    in
    {
      # Export overlays so that importing flakes can use them
      overlays = overlays;

      packages = {
        # Create default package using system's python version
        maillog = pkgsWithOverlays.maillog { python = pkgsWithOverlays.python3; };
        default = self.packages.${system}.maillog;
      };

      devShells.default = pkgsWithOverlays.mkShell {
        inputsFrom = [ self.packages.${system}.default ];
        packages = with pkgsWithOverlays; [ poetry self.packages.${system}.default ];
      };
    }
  );
}
