import batou.vfs
import pytest
from risclog.batou.docserver import DocServer


@pytest.fixture
def docserver(root):
    env = root.environment
    env.vfs_sandbox = batou.vfs.Developer(root.environment, None)

    docserver = DocServer()
    root.component += docserver

    root.component.configure()
    return docserver


def test_returns_docserver_url(docserver, root):
    root.component.deploy()
    assert 'http://127.0.0.1:8095/convertToPDF' == docserver.docserver_url


def test_creates_check_http_nagios_service(docserver, root):
    root.component.deploy()

    service = docserver.sub_components[0]

    assert (
        'check_http -w 3 -c 5 -I 127.0.0.1 -p 8095 --url /convertToPDF -t 3 '
        '-w 3 -c 5 --header=content-type:application/json --method=POST '
        '--post=\'{"convertToPDF": {"input": "asdf"}}\''
    ) == service.command
