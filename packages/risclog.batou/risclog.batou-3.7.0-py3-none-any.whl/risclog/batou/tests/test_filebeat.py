import os

import batou.vfs
import pytest
from batou.component import Component
from risclog.batou.filebeat import Filebeat


class Provider(Component):
    def configure(self):
        self.provide(
            'log_paths',
            [
                (
                    'instance',
                    '/tmp/log.txt',
                    None,
                    r'^\d{4}\-(0[1-9]|1[012])\-(0[1-9]|[12][0-9]|3[01])',  # noqa
                    None,
                )
            ],
        )


@pytest.fixture
def filebeat(root):
    env = root.environment
    env.vfs_sandbox = batou.vfs.Developer(root.environment, None)
    log_paths = Provider()
    root.component += log_paths
    filebeat = Filebeat(
        filebeat_cloud_id='<cloud_id>',
        filebeat_cloud_auth='<username>:<password>',
        filebeat_app='risclog.batou',
        filebeat_stage='pytest',
    )
    root.component += filebeat

    root.component.configure()
    root.component.deploy()
    return filebeat


@pytest.mark.skipif(
    condition=bool(os.environ.get('CI_TEST_RUN', 0)),
    reason='nix commands not available under ubuntu.',
)
def test_filebeat_generates_nix_config(filebeat):
    config = filebeat.sub_components[0]
    with open(config.path, encoding=config.encoding) as f:
        result = f.read()
        assert [li for li in result.splitlines() if li.strip()] == [
            '{ lib, pkgs, ... }:',
            '{',
            '  services.filebeat = {',
            '    enable = true;',
            '    package = pkgs.filebeat7-oss;',
            '    # ensure there is a `modules` subdirectory in the package, to check',  # noqa
            '    # whether an error message is actually an issue',
            '    settings.setup.ilm.rollover_alias = "risclog.batou-pytest";',
            '    settings.cloud.id = "<cloud_id>";',
            '    settings.cloud.auth = "<username>:<password>";',
            '    settings.output.elasticsearch = {',
            '      hosts = [ '
            '"https://6819b3f56a574f2c87e24ae9c78e7ab4.eu-central-1.aws.cloud.es.io" ];',  # noqa
            '    };',
            '    inputs.log0 = {',
            '      type = "filestream";',
            '      id = "log0";',
            '      enabled = true;',
            '      paths = [ "/tmp/log.txt" ];',
            '      multiline = {',
            '        pattern = "^\\d{4}\\-(0[1-9]|1[012])\\-(0[1-9]|[12][0-9]|3[01])";',  # noqa
            '        negate = true;',
            '        match = "after";',
            '      };',
            '      fields = {',
            '        log_type = "instance";',
            '        environment = "pytest";',
            '        app = "risclog.batou";',
            '      };',
            '    };',
            '  };',
            '}',
        ]
