import batou.component
import batou.lib.archive
import batou.lib.download
import batou.lib.file
import batou.lib.service
import batou_ext.nix
import pkg_resources


class Log(object):
    def __init__(
        self,
        name,
        type,
        path,
        processors='',
        multiline=False,
        exclude_lines=None,
    ):
        self.name = name
        self.type = type
        self.path = path
        self.processors = processors
        self.multiline = multiline
        self.exclude_lines = exclude_lines


@batou_ext.nix.rebuild
class Filebeat(batou.component.Component):

    filebeat_host = (
        'https://6819b3f56a574f2c87e24ae9c78e7ab4.eu-central-1.aws.cloud.es.io'
    )
    filebeat_cloud_id = None
    filebeat_cloud_auth = None
    filebeat_app = None
    filebeat_stage = None

    def configure(self):
        self.data = []

        self.log_paths = self.require('log_paths', host=self.host)
        i = 0
        for paths in self.log_paths:
            for type, path, processors, multiline, exclude in paths:
                self.data.append(
                    Log(
                        'log{}'.format(i),
                        type,
                        path,
                        processors,
                        multiline,
                        exclude,
                    )
                )
                i += 1

        self += batou.lib.file.File(
            '/etc/local/nixos/filebeat.nix',
            source=pkg_resources.resource_filename(
                'risclog.batou', 'resources/filebeat.nix'
            ),
        )

        # Remove old stuff
        self += batou_ext.nix.PurgePackage('filebeat')
        self += batou.lib.file.Purge('filebeat')
        self += batou.lib.file.Purge('filebeat.nix')
        self += batou.lib.file.Purge('filebeat.yml')
        self += batou.lib.file.Purge('/etc/local/systemd/filebeat.service')
