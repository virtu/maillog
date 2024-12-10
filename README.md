# maillog

A simple python mail logging framework, consisting of:
- `maillogd`, a daemon that accept and stores log events via a simple API.
  The daemon sends daily summary emails with all events logged on a given day.
- `maillog`, a python package that simplifies email logging via python. `maillog`
  implements the `maillogd` API and abstracts it using a simple interface:

  ```python
  import maillog
  
  # log warning event
  maillog.warning("This should not happen.")
  
  # log error event
  maillog.error("An error occurred.")
  ```

- `maillog-cli`, a simple command-line tool to interact with `maillogd`. The tool can be
  used to send events to `maillogd` and request a snapshot of all buffered messages:

  ```bash
  # send log event from the command line
  maillog-cli event "This is a warning from maillog-cli"

  # get events buffered on server
  maillog-cli status

## Installation and setup

This software provides a Nix flake along with a NixOS module. The recommended approach
is to use the flake as input of a NisOS configuration and enable the module:

```nix
sops.secrets."maillog/smtp-pass" = { }; # sops secret with SMTP account password
services.maillog = {
  enable = true;

  # email configuration
  schedule = "23:00";         # time [UTC] when to send daily summary emails
  from = "maillog@acme.com";  # sender
  to = "alerts@acme";         # recipient
  server = "smtp.acme.com";   # SMTP server
  port = 587;                 # SMTP port
  username = "maillog-user";  # SMTP account username
  passwordFile = config.sops.secrets."maillog/smtp-pass".path; # file containing SMTP account password
  };

```
