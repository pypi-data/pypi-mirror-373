from batou.component import Attribute, Component
from batou.lib.file import File


class BashEnv(Component):

    editor = Attribute(str, default='vim')
    pager = Attribute(str, default='cat')

    def configure(self):
        self += File(
            '~/.bash_profile',
            content="""\
EDITOR={{component.editor}}
PAGER={{component.pager}}
""",
        )
