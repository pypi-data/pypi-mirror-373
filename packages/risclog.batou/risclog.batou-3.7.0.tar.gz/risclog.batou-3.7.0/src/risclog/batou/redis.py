from telnetlib import Telnet

import batou_ext.nix
from batou.component import Component
from batou.lib.file import File
from batou.utils import Address


@batou_ext.nix.rebuild
class Redis(Component):
    """Export redis address.

    This component assumes that redis is already running. We just
    export the address with the `redis` resource.

    """

    listen_port = '6379'
    password = ''

    def configure(self):
        self.address = Address(self.host.fqdn, self.listen_port)

        self.provide(
            'redis_address', f'redis://:{self.password}@{self.address}/0'
        )

        self += File(
            '/etc/local/redis/password',
            content=self.password,
            sensitive_data=True,
        )

    def verify(self):
        self.redis_control = Telnet('localhost', self.listen_port)
        self.assert_no_subcomponent_changes()

    def update(self):
        self.redis_control.write(b'flush_all\n')
        self.redis_control.close()
