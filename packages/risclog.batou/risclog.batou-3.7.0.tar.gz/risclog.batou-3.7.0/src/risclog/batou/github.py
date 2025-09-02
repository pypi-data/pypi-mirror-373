import batou.component
import batou.lib.file


class GithubReleaseDownload(batou.component.Component):

    namevar = 'version'
    package = None
    file = None
    gh_oauth_user = 'claimxro'
    gh_oauth_token = None

    def configure(self):
        if not self.package:
            raise KeyError('No package is given')
        self.provide('package', 'gitAndTools.gh')
        if self.gh_oauth_token:
            self += batou.lib.file.Directory('~/.config/')
            self += batou.lib.file.Directory('~/.config/gh/')
            self.config = batou.lib.file.File(
                '~/.config/gh/config.yml',
                content="""\
git_protocol: https
editor:
prompt: enabled
pager:
aliases:
    co: pr checkout
http_unix_socket:
browser:""",
                mode=0o644,
            )
            self += self.config
            self.hosts = batou.lib.file.File(
                '~/.config/gh/hosts.yml',
                content=f"""\
github.com:
    oauth_token: {self.gh_oauth_token}
    user: {self.gh_oauth_user}
    git_protocol: ssh""",
                mode=0o644,
            )
            self += self.hosts

    def verify(self):
        raise batou.UpdateNeeded()

    def update(self):
        self.cmd(
            f'gh release download --repo risclog-solution/{self.package} '
            f'{self.version} -p {self.file} --clobber -D /tmp'
        )

    @property
    def namevar_for_breadcrumb(self):
        return f'{self.package}/{self.version}'
