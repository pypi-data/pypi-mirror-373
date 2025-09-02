import getpass
import os

import batou.vfs
import pytest
from risclog.batou.proftpd import FTPServer


@pytest.fixture
def ftpserver(root):
    env = root.environment
    env.vfs_sandbox = batou.vfs.Developer(root.environment, None)
    env.service_user = getpass.getuser()
    os.environ['LOCALE_ARCHIVE'] = 'C.UTF-8'
    os.environ['TZDIR'] = '/tmp/'

    ftpserver = FTPServer()
    ftpserver.server_name = 'localhost'
    ftpserver.hostkey = 'asdf'
    ftpserver.config_dir = '/tmp/'
    root.component += ftpserver

    root.component.configure()
    return ftpserver


def test_returns_ftpserver_url(ftpserver, root):
    root.component.deploy()
    assert '127.0.0.1' == ftpserver.ftp_address.listen.host
    assert '21' == ftpserver.ftp_address.listen.port
    assert '127.0.0.1' == ftpserver.sftp_address.listen.host
    assert '2222' == ftpserver.sftp_address.listen.port


def test_creates_check_ftp_nagios_service(ftpserver, root):
    root.component.deploy()

    assert [
        'check_ssh -4 -p 2222 localhost',
        'check_ssh -6 -p 2222 localhost',
        'check_ftp -4 localhost',
        'check_ftp -6 localhost',
    ] == [s.command for s in ftpserver.sub_components[-4:]]
