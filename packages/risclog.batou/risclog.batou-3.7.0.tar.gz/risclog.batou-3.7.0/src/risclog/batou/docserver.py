import batou.lib.file
import batou_ext.nix
import pkg_resources
from batou.component import Component
from batou.lib.appenv import AppEnv
from batou.lib.nagios import Service
from batou.utils import Address

from .restart import Restart

SENSU_COMMAND = (
    'check_http -w 3 -c 5 -I %s -p %s --url %s -t 3 -w 3 -c 5 '
    '--header=content-type:application/json '
    '--method=POST '
    '--post=\'{\"convertToPDF\": {\"input\": \"asdf\"}}\''
)


class DocServer(Component):

    listen_port = 8095
    command_path = '/convertToPDF'
    libre_cmd = 'soffice'
    libre_timeout = 60
    py3_version = '3.10'
    install_python = True

    def configure(self):
        self.address = Address(self.host.fqdn, self.listen_port)
        self += Service(
            'docserver',
            name='docserver',
            contact_groups=['risclog'],
            command=SENSU_COMMAND
            % (
                self.address.listen.host,
                self.address.connect.port,
                self.command_path,
            ),
        )
        self.docserver_url = 'http://{}:{}{}'.format(
            self.address.listen.host,
            self.address.connect.port,
            self.command_path,
        )
        self.provide('docserver', self.docserver_url)
        self.provide('docserver:http', self.address)

        self += batou.lib.file.File(
            '/etc/local/nixos/fonts.nix',
            source=pkg_resources.resource_filename(
                'risclog.batou', 'resources/docserver/fonts.nix'
            ),
        )
        packages = ['libreoffice']
        if self.install_python is True:
            packages.append('libffi')
            packages.append(
                'python{}Full'.format(self.py3_version.replace('.', ''))
            )

        if self.host.platform == 'nixos':
            self += batou_ext.nix.UserEnv(
                'libreoffice',
                channel=(
                    'https://hydra.flyingcircus.io/build/10503246/'
                    'download/1/nixexprs.tar.xz'
                ),
                packages=packages,
                ignore_collisions=True,
            )

        with open('requirements.lock', 'w') as f:
            f.write(
                open(
                    pkg_resources.resource_filename(
                        'risclog.batou',
                        'resources/docserver/requirements.lock',
                    )
                ).read()
            )

        appenv = AppEnv(self.py3_version, pip_version='21.1')
        self += appenv

        self += batou.lib.file.File(
            'portal.ini',
            source=pkg_resources.resource_filename(
                'risclog.batou', 'resources/docserver/portal.ini'
            ),
        )

        checksum = appenv.env_hash

        self += batou.lib.service.Service(
            'docserver',
            checksum=checksum,
            systemd=dict(
                Type='simple',
                ExecStart=self.expand(
                    '{{component.workdir}}/bin/pserve '
                    '{{component.workdir}}/portal.ini'
                ),
                Restart='always',
            ),
        )
        self += Restart('docserver')
