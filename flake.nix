{
  description = "A Bitcoin DNS seeder supporting all network types";

  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-23.11";
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, flake-utils, poetry2nix }: {
    nixosModules.maillog = import ./module.nix self;
  } // flake-utils.lib.eachDefaultSystem (system:
    let
      pkgs = nixpkgs.legacyPackages.${system};
      inherit (poetry2nix.lib.mkPoetry2Nix { inherit pkgs; }) mkPoetryApplication;
    in
    {
      packages = {
        maillogd = mkPoetryApplication {
          projectDir = ./.;
          mainProgram = "maillogd";
        };
        maillog-cli = mkPoetryApplication {
          projectDir = ./.;
          mainProgram = "maillog-cli";
        };
        default = self.packages.${system}.maillogd;
      };

      devShells.default = pkgs.mkShell {
        inputsFrom = [ self.packages.${system}.default ];
        packages = with pkgs; [ poetry ];
      };
    });
}
