import batou.component
import batou_ext.nix


class UserEnv(batou.component.Component):
    """UserEnv Komponente, die Package Requirements aus allen Komponenten
     aggregiert.

     Usage in den Komponenten:

      def configure(self):
          self.provide('package', 'imagemagick7Big')
          self.provide('package', 'qpdf')
          self.provide('package', 'ghostscript')
          self.provide('package_attribute', 'nixos.wkhtmltopdf_0_12_5')

    Hinweise:

      Auflisten aller UserEnvs:
          `nix-env -q`
      Löschen eines UserEnvs:
          `nix-env -e <userenv>`
    """

    name = 'package'
    channel = (
        'https://hydra.flyingcircus.io/build/378017/download/1/nixexprs.tar.xz'
    )
    ignore_collisions = False

    def configure(self):
        self.packages = self.require(
            self.name, host=self.host, reverse=True, strict=False
        )
        # Make unique
        self.packages = sorted(set(self.packages))

        self += batou_ext.nix.UserEnv(
            self.name,
            channel=self.channel,
            packages=self.packages,
            ignore_collisions=self.ignore_collisions,
        )

        self.package_attributes = self.require(
            self.name + '_attribute',
            host=self.host,
            reverse=True,
            strict=False,
        )
        # Make unique
        self.package_attributes = sorted(set(self.package_attributes))
        for attrib in self.package_attributes:
            self += batou_ext.nix.Package(attribute=attrib)
