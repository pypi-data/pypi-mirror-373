import batou.utils
import pytest


def test_github_release_download(root):
    from risclog.batou.github import GithubReleaseDownload

    env = root.environment
    env.vfs_sandbox = batou.vfs.Developer(root.environment, None)
    grd = GithubReleaseDownload(
        '1.0',
        package='risclog.frontend',
        file='claimx.zip',
        gh_oauth_token='<SECRET>',
    )
    root.component += grd
    with pytest.raises(batou.utils.CmdExecutionError) as e:
        root.component.deploy()

    assert e.value.cmd == (
        'gh release download --repo risclog-solution/risclog.frontend '
        '1.0 -p claimx.zip --clobber -D /tmp'
    )

    assert (
        """\
git_protocol: https
editor:
prompt: enabled
pager:
aliases:
    co: pr checkout
http_unix_socket:
browser:"""
        == open(grd.config.path, 'r').read()
    )

    assert (
        """\
github.com:
    oauth_token: <SECRET>
    user: claimxro
    git_protocol: ssh"""
        == open(grd.hosts.path, 'r').read()
    )
