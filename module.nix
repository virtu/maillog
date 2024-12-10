flake: { config, pkgs, lib, ... }:

with lib;

let
  inherit (flake.packages.${pkgs.stdenv.hostPlatform.system}) maillog;
  cfg = config.services.maillog;
in
{
  options.services.maillog = {
    enable = mkEnableOption "maillog";
    client.enable = mkEnableOption "client functionality (darkdig)";
    tor.enable = mkEnableOption "maillog via TOR";
    i2p.enable = mkEnableOption "maillog via I2P";
    cjdns = {
      enable = mkEnableOption "maillog via CJDNS";
      address = mkOption {
        type = types.nullOr types.str;
        default = null;
        example = "fcf9:45bc:8c48:6973:7b3f:5538:6e51:8fc9";
        description = mdDoc "Address used by CJDNS server.";
      };
    };

    logLevel = mkOption {
      type = types.str;
      default = "INFO";
      example = "DEBUG";
      description = mdDoc "Log verbosity for console.";
    };

    port = mkOption {
      type = types.int;
      default = 53;
      example = 8053;
      description = mdDoc "Port used by DNS server.";
    };
    address = mkOption {
      type = types.str;
      default = "127.0.0.1";
      example = "192.168.0.1";
      description = mdDoc "Address used by DNS server.";
    };
    zone = mkOption {
      type = types.nullOr types.str;
      default = null;
      example = "dnsseed.acme.com.";
      description = mdDoc "Zone managed by DNS server.";
    };
  };

  config = mkIf cfg.enable {
    assertions = [
      { assertion = !(cfg.client.enable && (!cfg.tor.enable || !cfg.i2p.enable)); message = "services.maillog.client.enable requires services.maillog.tor and services.maillog.i2p to be enabled."; }
      { assertion = !(cfg.cjdns.enable && cfg.cjdns.address == null); message = "services.maillog.cjdns.address must be set when services.maillog.cjdns.enable is true."; }
      { assertion = cfg.zone != null; message = "services.maillog.zone must be set."; }
    ];

    environment.systemPackages = lib.optional cfg.cjdns.enable pkgs.socat ++
      lib.optional cfg.client.enable flake.packages.${pkgs.stdenv.hostPlatform.system}.darkdig;

    networking.firewall = {
      allowedUDPPorts = [ cfg.port ];
      allowedTCPPorts = [ cfg.port ];
    };

    services.fail2ban = {
      enable = true;
      jails = {
        maillog = {
          settings = {
            backend = "systemd";
            journalmatch = "_SYSTEMD_UNIT=maillog.service + _COMM=maillog";
            filter = "maillog";
            # rate limit to ten requests per minute; ban for one hour, both udp and tcp
            maxretry = 10;
            findtime = 60;
            bantime = 3600;
            protocol = "tcp,udp";
          };
        };
      };
    };
    environment.etc."fail2ban/filter.d/maillog.conf".text = /* ini */ ''
      [Definition]
      # match all lines containing ban=<SUBNET>, except from debug log
      failregex = ^.*ban=<SUBNET>.*$
      ignoreregex = ^.* DEBUG .*$
    '';

    # Make DNS server reachable via TOR
    services.tor = mkIf cfg.tor.enable {
      client.enable = mkIf cfg.client.enable true;
      torsocks.enable = mkIf cfg.client.enable true;
      enable = true;
      enableGeoIP = false;
      relay.onionServices = {
        maillog = {
          version = 3;
          map = [
            { port = cfg.port; target = { addr = "${cfg.address}"; port = cfg.port; }; }
          ];
        };
      };
    };

    # Make DNS server reachable via I2P
    services.i2pd = mkIf cfg.i2p.enable {
      proto.socksProxy.enable = mkIf cfg.client.enable true;
      enable = true;
      inTunnels.maillog-dns = {
        enable = true;
        inPort = cfg.port;
        destination = cfg.address;
        address = cfg.address;
        port = cfg.port;
      };
    };

    # Make DNS server reachable via CJDNS
    systemd.services.darkdig-cjdns-udp-socat-proxy = mkIf cfg.cjdns.enable {
      description = "Forward TCP UDP to CJDNS using socat";
      wantedBy = [ "multi-user.target" ];
      serviceConfig = {
        ExecStart = "${pkgs.socat}/bin/socat UDP6-LISTEN:${toString cfg.port},bind='[${cfg.cjdns.address}]',fork,su=nobody UDP4:${cfg.address}:${toString cfg.port}";
        Restart = "always";
      };
    };

    systemd.services.maillog = {
      description = "maillog";
      wants = [ "network-online.target" ];
      after = [ "network-online.target" ];
      wantedBy = [ "multi-user.target" ];
      serviceConfig = {
        ExecStart = ''${maillog}/bin/maillog \
            --log-level ${cfg.logLevel} \
            --address ${cfg.address} \
            --port ${toString cfg.port} \
            --zone ${cfg.zone} \
          '';
        AmbientCapabilities = "CAP_NET_BIND_SERVICE";
        DynamicUser = true;
      };
    };
  };
}
