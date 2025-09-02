{ lib, ... }:

{
    services.nscd.enable = lib.mkForce false;
    system.nssModules = lib.mkForce [];
    systemd.services.nscd.enable = false;
}
