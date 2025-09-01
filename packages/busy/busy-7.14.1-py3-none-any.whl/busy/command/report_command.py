import re

from jinja2.sandbox import SandboxedEnvironment

from busy.command import CollectionCommand, MultiCollectionCommand
from busy.error import BusyError
from busy.model.item import Item

from wizlib.parser import WizParser


class ReportCommand(MultiCollectionCommand):
    """Output items using a defined string format."""

    name = 'report'

    @classmethod
    def add_args(cls, parser: WizParser):
        super().add_args(parser)
        parser.add_argument('--line', '-l')

    @CollectionCommand.wrap
    def execute(self):
        items = self.selection
        result = [self.formatted(x, m) for x, m in items]
        return '\n'.join(result)

    def formatted(self, index, item):
        # return self.line.format(**vars(item))
        template = SandboxedEnvironment().from_string(self.line)
        return template.render(item.formattable)
