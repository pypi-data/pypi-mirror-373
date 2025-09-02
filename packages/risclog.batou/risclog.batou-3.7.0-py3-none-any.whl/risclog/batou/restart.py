import batou


class Restart(batou.component.Component):

    service = batou.component.Attribute()
    namevar = 'service'

    def verify(self):
        if 'testing' in self.environment.name:
            raise batou.UpdateNeeded()

    def update(self):
        self.cmd(f'sudo systemctl restart {self.service}.service')
