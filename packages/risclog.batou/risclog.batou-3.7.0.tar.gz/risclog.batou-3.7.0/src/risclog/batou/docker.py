import hashlib
import os
import stat

import batou
import batou.lib.file
import pkg_resources
from batou.component import Attribute, Component
from batou.lib.cron import CronJob


class DockerEnvItem:
    key = None
    value = None

    def __init__(self, key, value):
        self.key = key
        self.value = value


class Docker(Component):

    package = Attribute(str)
    version = Attribute(str)
    path = Attribute(str)
    reponame = Attribute(str)

    use_traefik = Attribute(bool, default=True)
    strip_prefix = Attribute(bool, default=False)
    use_iam = Attribute(bool, default=True)
    use_s3 = Attribute(bool, default=True)
    use_alembic = Attribute(bool, default=True)
    database_name = Attribute(str, default=None)

    allowed_origins = Attribute(str, default='')
    allowed_referrer = Attribute(str, default='')

    keystore_dir = None
    public_name = None
    public_url = None
    service_port = 8000

    registry_url = 'registry.claimx.net'
    registry_port = 5000

    docker_path = '/run/current-system/sw/bin/docker'
    Dockerfile = 'Dockerfile'
    docker_env = None

    cronjobs = {}  # key: cronjob command, value: crontab timing

    def _cronjob_file(self, cronjob):
        filename = f'{cronjob.replace(" ", "_").lower()}.sh'
        return os.path.join(self.workdir, filename)

    def get_iam(self):
        self.iam = self.require_one('iam')
        name = self.package.split('.')[-1]
        self.iamclient = self.require_one(f'{name}keycloakclient')

    def configure(self):
        if self.use_traefik:
            self.traefik = self.require_one('traefik')
            self.public_name = self.traefik.public_name
            self.public_url = self.traefik.public_url
        if self.use_iam:
            self.get_iam()
        if self.use_s3:
            self.s3 = self.require_one('s3')

        checksum = hashlib.sha256()

        if os.path.exists(f'{self.defdir}/keystore.config'):
            self.keystore_dir = batou.lib.file.Directory('keystore')
            self += self.keystore_dir
            self += batou.lib.file.File(
                os.path.join(self.keystore_dir.path, '.keystore.config'),
                source='keystore.config',
            )
            checksum.update(self._.content)
            self += batou.lib.file.File(
                os.path.join(self.keystore_dir.path, '.keystore.store'),
                source='keystore.store',
            )
            checksum.update(self._.content)

        if self.database_name:
            self.db = self.require_one(self.database_name)

        if self.environment.name == 'dev' and self.reponame:
            source = self.require_one('source')
            self.checkout_path = source.clones[self.reponame].target
            self.data_path = self.reponame.replace('service', 'data').replace(
                '.', '/'
            )
            self.alembic_ini_path = os.path.join(
                self.checkout_path, 'alembic.ini'
            )
            if self.use_alembic:
                self += batou.lib.file.File(
                    self.alembic_ini_path,
                    source=pkg_resources.resource_filename(
                        'risclog.batou', 'resources/alembic.ini'
                    ),
                )

        self.service_name = self.package.replace('.', '_')
        self.registry_path = self.package.replace('.', '/')
        self.container_name = (
            self.package.replace('.', '-')
            + '-'
            + self.version.replace('.', '')
        )
        self.service_path = self.path
        self.service_version = self.version

        self.service_file = batou.lib.file.File(
            'service.yml',
            source=pkg_resources.resource_filename(
                'risclog.batou', 'resources/service.yml'
            ),
        )
        self += self.service_file
        checksum.update(self._.content)

        if self.environment.name == 'dev' and self.reponame:
            self += batou.lib.file.File(
                'publish',
                source=pkg_resources.resource_filename(
                    'risclog.batou', 'resources/publish.sh'
                ),
                mode=0o755,
            )

        self += batou.lib.service.Service(
            self.service_name.split('_')[-1],
            systemd=dict(
                ExecStart=self.expand(
                    f'{self.docker_path}-compose '
                    '-f {{component.service_file.path}} up'
                ),
                Restart='always',
                Type='simple',
            ),
            checksum=checksum.hexdigest(),
        )

        for cronjob, timing in self.cronjobs.items():
            self += CronJob(self._cronjob_file(cronjob), timing=timing)

    def verify(self):
        raise batou.UpdateNeeded()

    def update(self):
        if self.environment.name == 'dev':
            if self.reponame:
                self.cmd(
                    f'{self.docker_path} stop $('
                    f'{self.docker_path} ps -aqf '
                    f'"name=^{self.container_name}$")',
                    ignore_returncode=True,
                )
                self.cmd(
                    f'{self.docker_path}-compose -p {self.container_name} '
                    f'-f {self.service_file.path} up --build -d'
                )
            else:
                self.cmd(
                    f'{self.docker_path}-compose '
                    '-f {{component.service_file.path}} up -d'
                )

        stdout, err = self.cmd(
            f'{self.docker_path} ps -aqf "name=^{self.container_name}$"'
        )
        self.containers = containers = stdout.split()

        if len(containers) == 1:
            for container in containers:
                for cronjob in self.cronjobs.keys():
                    filename = self._cronjob_file(cronjob)
                    with open(filename, 'w') as f:
                        f.write(
                            f'{self.docker_path} exec {container} {cronjob}',
                        )
                    st = os.stat(filename)
                    os.chmod(filename, st.st_mode | stat.S_IEXEC)

        if self.use_alembic:
            self.run_alembic()

    def run_alembic(self):
        containers = self.containers
        if len(containers) < 1:
            return

        for container in containers:
            self.cmd(
                f'{self.docker_path} exec {container} alembic upgrade head'
            )
