import hashlib
import os

import batou
import batou.component
import batou.lib.archive
import batou.lib.download
import batou.lib.service
import batou_ext.config
import batou_ext.nix
import batou_ext.postgres
import pkg_resources
from batou.component import Attribute, Component
from batou_ext.postgres import PostgresServer  # noqa


class Postgres_Keycloak(Component):

    db_user = 'keycloak-user'
    db_pass = Attribute(str)
    db_name = 'keycloak'
    _command_prefix = 'sudo -u postgres'

    def configure(self):
        self.db_address = self.require_one('postgres').address
        self += batou_ext.postgres.User(
            self.db_user,
            password=self.db_pass,
            command_prefix=self._command_prefix,
        )
        self += batou_ext.postgres.DB(
            self.db_name,
            owner=self.db_user,
            command_prefix=self._command_prefix,
        )

        self.provide('postgres_keycloak', self)

    def verify(self):
        self.assert_no_subcomponent_changes()


@batou_ext.nix.rebuild
class Keycloak(batou.component.Component):

    version = '26.2.5'
    checksum = 'sha1:b0f6aa48625a090713ca0964cad47846af84ebc3'
    postgresql_version = '42.5.1'
    postgresql_checksum = 'md5:378f8a2ddab2564a281e5f852800e2e9'
    openjdk_version = 'openjdk17'
    hostname = Attribute(str)
    hostname_admin = Attribute(str)
    listen_port = 8088
    admin_password = Attribute(str, default=None)
    welcome_theme = Attribute(str, default=None)
    additional_themes = Attribute(str, default=None)
    userenv = Attribute(str, default='package')
    role = None
    possible_roles = [
        'main',
        'backup',
    ]
    features = possible_roles[:]

    def _compute_role(self):
        role = set(self.features).intersection(self.possible_roles)
        if len(role) == 1:
            self.role = role.pop()
        else:
            self.role = ''

    @property
    def name(self):
        return self.expand('keycloak-{{component.host.name}}')

    def configure(self):
        self._compute_role()
        self.provide('keycloak', self)
        self.postgresql = self.require_one('postgres_keycloak')
        # Keycloak opens more ports, but we are currently interested
        # int he http port
        self.address = batou.utils.Address(
            self.host.fqdn, self.listen_port, require_v6=True
        )
        self.provide('mail_send_host', self)

        self._download_and_unpack()
        if self.environment.platform == 'nixos':
            self.provide(self.userenv, self.openjdk_version)

        checksum = hashlib.new('sha256')

        self += batou.lib.file.File(
            self.expand('{{component.basedir}}/conf/keycloak.conf'),
            source=pkg_resources.resource_filename(
                'risclog.batou', 'resources/keycloak/keycloak.conf'
            ),
        )
        checksum.update(self._.content)

        self += batou.lib.file.BinaryFile(
            self.expand(
                '{{component.basedir}}/providers/'
                'keycloak-last-login-event-listener.jar'
            ),
            source=pkg_resources.resource_filename(
                'risclog.batou',
                'resources/keycloak/keycloak-last-login-event-listener.jar',
            ),
        )
        checksum.update(self._.content)

        # Copy themes
        if self.additional_themes:
            themes_dir = os.path.normpath(
                os.path.join(self.root.defdir, self.additional_themes)
            )
            for theme in os.listdir(themes_dir):
                source = os.path.join(themes_dir, theme)
                if not os.path.isdir(source):
                    continue
                self += batou.lib.file.Directory(
                    self.expand('{{component.basedir}}/themes/' + theme),
                    source=source,
                )

        self += batou.lib.file.File(
            'keycloak',
            mode=0o755,
            source=pkg_resources.resource_filename(
                'risclog.batou', 'resources/keycloak/keycloak.sh'
            ),
        )
        checksum.update(self._.content)

        self += batou_ext.config.RegexPatch(
            (f'{self.workdir}/keycloak-{self.version}/bin/kc.sh'),
            pattern=('#!/bin/bash'),
            replacement=('#!/bin/sh'),
        )

        self += batou.lib.service.Service(
            self.map('keycloak'),
            checksum=checksum.hexdigest(),
            systemd=dict(Type='simple', Restart='always'),
        )

    def _download_and_unpack(self):
        self += batou.lib.file.Directory('downloads')
        self += batou.lib.download.Download(
            self.expand(
                'https://github.com/keycloak/keycloak/releases/download/'
                '{{component.version}}/keycloak-{{component.version}}.tar.gz'
            ),
            checksum=self.checksum,
            target='downloads/keycloak.tar.gz',
        )
        self += batou.lib.archive.Extract(self._.target, target='.')
        self.basedir = self.map(self.expand('keycloak-{{component.version}}'))
