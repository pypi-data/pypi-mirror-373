import grp
import hashlib
import os
import pwd

import batou
import batou.c
import batou.component
import batou.lib.file
import batou.lib.nagios
import batou.utils
import batou_ext.nix
import pkg_resources


class FTPServer(batou.component.Component):
    """Install and configure ProFTPd with virtual user support from
    workdir/ftpd.passwd.
    See update method docstring for how to add users.
    """

    hostkey = """\
-----BEGIN EC PRIVATE KEY-----
MHcCAQEEIPJm5Ptvg5EgPAjE5BVFx6DnJ9BorINwMttZ10t4W/6KoAoGCCqGSM49
AwEHoUQDQgAENKPtivtSk6CMQp9y11MOrPRXGcanJvTvJF4enRbtaucYk0MjAaZT
52iJxFllu0ciFXSA5DQ94DYB1+knoj5zag==
-----END EC PRIVATE KEY-----"""
    hostkey_pub = (
        'ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYA'
        'AABBBDSj7Yr7UpOgjEKfctdTDqz0VxnGpyb07yReHp0W7WrnGJNDIwGmU+doicRZZbtH'
        'IhV0gOQ0PeA2AdfpJ6I+c2o= user@host'
    )

    home = '/srv/{user}/sftp-home'
    server_name = batou.component.Attribute(str)
    extended_debug = batou.component.Attribute(bool, default=False)

    def configure(self):
        """template ProFTPd configuration file."""
        self.ftp_address = f'{self.server_name}:21'
        self.sftp_address = f'{self.server_name}:2222'
        self.service_user = self.environment.service_user
        self.home = self.home.format(user=self.service_user)
        self.provide('ftpserver_name', self.server_name)

        # We use the service user's private key as ProFTPd's host key.
        self += batou.lib.file.File(
            'hostkey', mode=0o600, content=self.hostkey
        )
        self.hostkey_path = self._.path

        self += batou.lib.file.BinaryFile(
            'proftpd.patch',
            source=pkg_resources.resource_filename(
                'risclog.batou', 'resources/proftpd/proftpd.patch'
            ),
        )
        if self.host.platform == 'nixos':
            self += batou_ext.nix.UserEnv(
                'proftpd',
                packages=['proftpd'],
                channel=(
                    'https://hydra.flyingcircus.io/build/225011/download/1/'
                    'nixexprs.tar.xz'
                ),
                let_extra="""\
proftpd = stdenv.mkDerivation rec {
name = "proftpd-${version}";
version = "1.3.9rc2";
src = fetchurl {
    url = "ftp://ftp.proftpd.org/distrib/source/proftpd-${version}.tar.gz";
    sha256 = "0xhv11z43hkpnk71a5xnlfg7pc84jjx7nijv4l1p4wlzvkw3vv7z";
};
buildInputs = [
    pkgs.libcap
    pkgs.libsodium
    pkgs.openssl
    pkgs.zlib
    /*
    XXX aktuell benutzt dieses Paket einen 22.05 build.
    Sobald auf 22.11 oder neuer geupgraded wird, braucht man
    (perl.override { libxcrypt = pkgs.libxcrypt-legacy; })
    */
    pkgs.perl
];
patches = [ ./proftpd.patch ];
configureFlags = [
    "--enable-openssl"
    "--with-modules=mod_sftp"
];
postInstall = ''
    patchShebangs $out/bin
'';
enableParallelBuilding = true;
meta = {
    homepage =http://www.proftpd.org/;
    description = "Highly configurable GPL-licensed FTP server software";
};
};
""",
            )

        # Provide listen addresses for both, FTP and TFTP.
        self.ftp_address = batou.utils.Address(
            self.ftp_address, require_v6=True
        )
        self.sftp_address = batou.utils.Address(
            self.sftp_address, require_v6=True
        )

        # We want to run ProFTPd in the service user's contet. Gather user data
        self.service_user_uid = os.getuid()
        self.service_user_group = grp.getgrgid(
            pwd.getpwnam(self.service_user).pw_gid
        ).gr_name

        # Pre-touch virtual user password file to satify runtime dependency.
        # self += batou.lib.file.Presence("ftpd.passwd", mode=0o440)
        self += batou.lib.file.File('ftpd.passwd', mode=0o440, content='')
        self.passwd_file = self._

        # The actual ProFTPd config.
        self += batou.lib.file.File(
            'proftpd.conf',
            source=pkg_resources.resource_filename(
                'risclog.batou', 'resources/proftpd/proftpd.conf'
            ),
        )
        self.config_file = self._
        self.config_hash = hashlib.sha256(self.config_file.content).hexdigest()

        self.env = os.environ
        self += batou.lib.file.File(
            '/etc/local/systemd/proftpd.service',
            source=pkg_resources.resource_filename(
                'risclog.batou', 'resources/proftpd/proftpd.service'
            ),
        )
        self += batou.lib.file.File(
            '/etc/local/firewall/proftpd.firewall',
            source=pkg_resources.resource_filename(
                'risclog.batou', 'resources/proftpd/proftpd.firewall'
            ),
        )
        if self.host.platform == 'nixos':
            self += batou_ext.nix.Rebuild()

        self += batou.lib.file.File(
            '~/create_sftp_user',
            source=pkg_resources.resource_filename(
                'risclog.batou', 'resources/proftpd/create_sftp_user'
            ),
            mode=0o755,
        )
        self += batou.lib.file.File(
            '~/delete_sftp_user',
            source=pkg_resources.resource_filename(
                'risclog.batou', 'resources/proftpd/delete_sftp_user'
            ),
            mode=0o755,
        )

        # Create virtual users designated home
        self += batou.lib.file.Directory(self.home)

        # Service checks
        self += batou.lib.nagios.Service(
            'Proftpd SSH IPv4',
            name='proftpd_ssh_v4',
            command=self.expand(
                'check_ssh -4 -p {{component.sftp_address.connect.port}} '
                '{{component.sftp_address.connect.host}}'
            ),
        )
        self += batou.lib.nagios.Service(
            'Proftpd SSH IPv6',
            name='proftpd_ssh_v6',
            command=self.expand(
                'check_ssh -6 -p {{component.sftp_address.connect.port}} '
                '{{component.sftp_address.connect.host}}'
            ),
        )

        self += batou.lib.nagios.Service(
            'Proftpd FTP IPv4',
            name='proftpd_ftp_v4',
            command=self.expand(
                'check_ftp -4 {{component.ftp_address.connect.host}}'
            ),
        )
        self += batou.lib.nagios.Service(
            'Proftpd FTP IPv6',
            name='proftpd_ftp_v6',
            command=self.expand(
                'check_ftp -6 {{component.ftp_address.connect.host}}'
            ),
        )
