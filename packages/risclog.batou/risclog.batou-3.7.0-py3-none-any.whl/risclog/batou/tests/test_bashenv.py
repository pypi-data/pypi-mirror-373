import batou.vfs
import pytest
from risclog.batou.bashenv import BashEnv


@pytest.fixture
def bashenv(root):
    env = root.environment
    env.vfs_sandbox = batou.vfs.Developer(root.environment, None)
    bashenv = BashEnv(
        pager='less',
    )
    root.component += bashenv

    root.component.configure()
    root.component.deploy()
    return bashenv


def test_bashenv_generates_bash_config(bashenv):
    conf = bashenv.sub_components[0]

    assert conf.path.endswith('/.bash_profile')

    with open(conf.path, encoding=conf.encoding) as f:
        result = f.read()
        assert [li.strip() for li in result.splitlines() if li.strip()] == [
            'EDITOR=vim',
            'PAGER=less',
        ]
