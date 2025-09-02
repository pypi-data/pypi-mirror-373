import batou.vfs
import pytest
from risclog.batou.disablenscd import DisableNSCD


@pytest.fixture
def disablenscd(root):
    env = root.environment
    env.vfs_sandbox = batou.vfs.Developer(root.environment, None)
    disablenscd = DisableNSCD()
    root.component += disablenscd

    root.component.configure()
    root.component.deploy()
    return disablenscd


def test_disablenscd_generates_nix_config(disablenscd):
    config = disablenscd.sub_components[0]

    with open(config.path, encoding=config.encoding) as f:
        result = f.read()
        assert (
            result
            == """\
{ lib, ... }:

{
    services.nscd.enable = lib.mkForce false;
    system.nssModules = lib.mkForce [];
    systemd.services.nscd.enable = false;
}
"""
        )
