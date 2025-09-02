import batou.component
import batou_ext.nix
import pkg_resources
from batou.lib.file import File


@batou_ext.nix.rebuild
class DisableNSCD(batou.component.Component):
    """Disable NSCD to fix DNS resolution problems."""

    def configure(self):
        self += File(
            '/etc/local/nixos/disablenscd.nix',
            source=pkg_resources.resource_filename(
                'risclog.batou', 'resources/disablenscd.nix'
            ),
        )
