import os
import pathlib
from io import StringIO

import requirements
from batou import output
from batou.component import Component


class Requirements(Component):

    namevar = 'output_filename'
    find_links = None  # e.g. ['https://download.example.com']
    pipconf = None  # content of pip.conf file
    pinnings = None  # e.g. {'batou': '2.0', 'batou_scm': '0.6.3'}
    editable_packages = None  # e.g. {'batou': '/usr/dev/batou'}
    additional_requirements = None  # e.g. ['pytest', 'pytest-flake8']
    python_preferences = None  # e.g. ['3.8', '3.9']

    def userenvhash(self):
        return os.path.realpath(os.path.expanduser('~/.nix-profile'))

    def configure(self):
        locked = []
        if self.pipconf:
            home = os.path.expanduser('~')
            pathlib.Path(os.path.join(home, '.config/pip/')).mkdir(
                parents=True, exist_ok=True
            )
            with open(os.path.join(home, '.config/pip/pip.conf'), 'w') as f:
                f.write(self.pipconf)
        reqs = open('requirements.txt', 'r').read().splitlines()
        if self.additional_requirements:
            reqs = list(set(reqs + self.additional_requirements))

        pkgs_not_pinned = []
        for req in requirements.parse(StringIO('\n'.join(reqs))):
            already_pinned = '==' in [x[0] for x in req.specs]
            if req.name and self.pinnings and not already_pinned:
                name = req.name.lower().replace('_', '-')
                pinnings = dict()
                for k, v in self.pinnings.items():
                    pinnings[k.lower().replace('_', '-')] = v
                if name in pinnings:
                    req.specs = [('==', pinnings[name])]
                    req.name = name
                else:
                    pkgs_not_pinned.append(req.name)
            if self.editable_packages and req.name in self.editable_packages:
                if req.name in pkgs_not_pinned:
                    pkgs_not_pinned.remove(req.name)
                req.editable = True
                req.path = self.editable_packages[req.name]
                req.name = None
                req.specs = []

            name = req.name
            specs = ','.join(f'{i[0]}{i[1]}' for i in req.specs)
            extras = ','.join(sorted(req.extras))
            extras = f'[{extras}]' if extras else ''
            if not req.editable:
                line = f'{name}{extras}{specs}'
            elif req.path:
                line = f'-e{req.path}{extras}'
            elif req.uri and name:
                line = f'-e{req.uri}#egg={name}'
            elif req.uri:
                line = f'-e{req.uri}'
            else:
                line = req.line
            locked.append(line)

        if pkgs_not_pinned:
            output.warn('The following packages are not pinned: ')
            output.annotate(', '.join(pkgs_not_pinned))
        with open(self.output_filename, 'w') as f:
            f.write('# Created by batou. Do not edit manually.\n')
            if self.python_preferences:
                f.write(
                    '# appenv-python-preference: {}\n'.format(
                        ','.join(self.python_preferences)
                    )
                )

            f.write('# {}\n'.format(self.userenvhash()))
            if self.find_links:
                f.write('\n'.join(f'-f {link}' for link in self.find_links))
                f.write('\n')
            f.write('\n'.join(sorted(locked)))
            f.write('\n')


class Update(Component):

    package = None
    python = ['3.10', '3.11']

    def configure(self):
        source = self.require_one('source', host=self.host)
        portal_path = source.clones[self.package].target
        if os.path.exists(portal_path):
            self += Requirements(
                f'{portal_path}/requirements.txt',
                editable_packages={self.package: ' .'},
                additional_requirements=(source.additional_requirements),
                pinnings=source.pinnings,
                python_preferences=self.python,
            )
