flake: { config, pkgs, lib, ... }:

with lib;

let
  inherit (flake.packages.${pkgs.stdenv.hostPlatform.system}) maillog;
  cfg = config.services.maillog;
in
{
  options.services.maillog = {
    enable = mkEnableOption "maillog";
    from = mkOption {
      type = types.str;
      default = null;
      description = "The sender address for the maillog service.";
    };
    to = mkOption {
      type = types.str;
      default = null;
      description = "The recipient address for the maillog service.";
    };
    server = mkOption {
      type = types.str;
      default = null;
      description = "The SMTP server for the maillog service.";
    };
    port = mkOption {
      type = types.int;
      default = 587;
      description = "The port for the maillog service.";
    };
    username = mkOption {
      type = types.str;
      default = null;
      description = "The username for the maillog service.";
    };
    passwordFile = mkOption {
      type = types.str;
      default = null;
      description = "The password file for the maillog service.";
    };
    schedule = mkOption {
      type = types.str;
      default = "23:59";
      description = "The schedule for the maillog service, i.e. the UTC time when to send the daily summary mail (e.g. 22:00)";
    };
  };

  config = mkIf cfg.enable {
    assertions = [
      { assertion = cfg.from != null; message = "services.maillog.from must be set."; }
      { assertion = cfg.to != null; message = "services.maillog.to must be set."; }
      { assertion = cfg.server != null; message = "services.maillog.server must be set."; }
      { assertion = cfg.username != null; message = "services.maillog.username must be set."; }
      { assertion = cfg.passwordFile != null; message = "services.maillog.passwordFile must be set."; }
    ];

    environment.systemPackages = [
      (pkgs.python3.withPackages
        (ps: [ flake.packages.${pkgs.stdenv.hostPlatform.system}.maillog ])
      )
    ];

    systemd.services.maillog = {
      description = "maillog service";
      wants = [ "network-online.target" ];
      after = [ "network-online.target" ];
      wantedBy = [ "multi-user.target" ];

      serviceConfig = {
        ExecStart = ''
          ${maillog}/bin/maillogd \
            --from ${cfg.from} \
            --to ${cfg.to} \
            --server ${cfg.server} \
            --port ${toString cfg.port} \
            --username ${cfg.username} \
            --password-file ${cfg.passwordFile} \
            --schedule ${cfg.schedule}
        '';
        # create /var/lib/maillog and make it readable so maillog clients can
        # access the socket
        RuntimeDirectory = "maillog";
        RuntimeDirectoryMode = "0755";

        # create /var/lib/maillog for the persistent event buffer file and
        # ensure the directory is only accessible by the maillog user
        StateDirectory = "maillog";
        StateDirectoryMode = "0700";
      };
    };

  }; # config
}
