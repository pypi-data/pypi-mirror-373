import batou.vfs
import pytest
from risclog.batou.redis import Redis


@pytest.fixture
def redis(root):
    env = root.environment
    env.vfs_sandbox = batou.vfs.Developer(root.environment, None)
    redis = Redis(listen_port=6379, password='<password>')
    root.component += redis

    root.component.configure()
    return redis


def test_raises_exception_if_redis_server_not_listening(redis, root):
    root.component.sub_components[0].listen_port = 63790
    with pytest.raises(ConnectionRefusedError):
        root.component.deploy()


def test_raises_no_exception_if_redis_server_is_listening(redis, root):
    root.component.deploy()

    config = redis.sub_components[0]

    with open(config.path, encoding=config.encoding) as f:
        result = f.read()
        assert result == '<password>'
