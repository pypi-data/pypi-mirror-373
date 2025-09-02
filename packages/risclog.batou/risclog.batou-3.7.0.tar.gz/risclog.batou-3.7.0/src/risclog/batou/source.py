import ast
import os.path

import batou.lib.file
import pkg_resources
from batou import UpdateNeeded
from batou.component import Component
from batou.lib.file import File
from batou.lib.git import Clone
from batou_ext.ssh import ScanHost


class Source(Component):

    sources = []
    vcs_update = 'True'
    pipconf = None
    find_links = None
    username = None
    private_key = None
    develop = batou.component.Attribute('list', default='')

    @property
    def distributions(self):
        return self.clones

    @property
    def pinnings(self):
        result = dict()
        for pinning in open(f'{self.defdir}/versions.txt').read().split():
            pkg, version = pinning.split('==')
            result[pkg] = version
        return result

    @property
    def editable_packages(self):
        result = dict()
        for pkg in self.clones:
            key = pkg.replace('_', '-')
            result[key] = self.clones[pkg].target
        return result

    @property
    def additional_requirements(self):
        if self.environment.name in ('dev', 'test', 'local', 'devhost'):
            return open(f'{self.defdir}/dev-requirements.txt').read().split()

    def configure(self):
        self.vcs_update = ast.literal_eval(self.vcs_update)

        if self.username and self.private_key:
            self += ScanHost('github.com')
            self += File(
                '~/.gitconfig',
                content="""\
[user]
    email = support@risclog.com
    user = risclog

[github]
    user = {{component.username}}
""",
            )
            self += File(
                '~/.ssh/id_rsa_github',
                content=self.private_key,
                mode=0o600,
            )
            self += File(
                '~/.ssh/config',
                content="""\
Host github.com
 HostName github.com
 IdentityFile ~/.ssh/id_rsa_github""",
                mode=0o600,
            )
            path = os.path.expanduser('~/.ssh')
            if self.root.environment.vfs_sandbox:
                path = self.root.environment.vfs_sandbox.map(path)

        self.clones = dict(self.add_clone(url) for url in self.sources)
        self += batou.lib.file.File(
            'gita',
            mode=0o755,
            source=pkg_resources.resource_filename(
                'risclog.batou', 'resources/gita'
            ),
        )

        self.provide('source', self)

    __update_needed = None

    def verify(self):
        # This check incurs network access for each source checkout, so we
        # want to short-cut repeated calls.
        if self.__update_needed is None:
            try:
                super(Source, self).verify()
            except UpdateNeeded:
                self.__update_needed = True
            else:
                self.__update_needed = False
        if self.__update_needed:
            raise UpdateNeeded()

    def add_clone(self, url):
        url, _, parameter_list = url.partition(' ')
        parameters = {}
        parameters['target'] = list(filter(bool, url.split('/')))[-1]
        parameters.update(x.split('=') for x in parameter_list.split())
        if (
            'branch' not in parameters
            and 'revision' not in parameters
            and 'tag' not in parameters
        ):
            parameters['branch'] = 'master'

        vcs_update = self.vcs_update or 'revision' in parameters
        clone = Clone(
            url, vcs_update=vcs_update, clobber=vcs_update, **parameters
        )
        self += clone
        return parameters['target'], clone
