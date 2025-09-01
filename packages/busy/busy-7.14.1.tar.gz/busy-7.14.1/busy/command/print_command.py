

from wizlib.parser import WizParser

from busy.command import CollectionCommand
from busy.util.checklist import Checklist


class PrintCommand(CollectionCommand):
    """Generate a Checklist PDF"""

    full: bool = False
    default_filter = ["1-"]
    name = "print"

    @classmethod
    def add_args(cls, parser: WizParser):
        super().add_args(parser)
        parser.add_argument('--long', '-l', action='store_true')

    @CollectionCommand.wrap
    def execute(self):  # pragma: nocover
        if self.long:
            tasks = [i.markup for i in self.selected_items]
        else:
            tasks = [i.base for i in self.selected_items]
        queue = self.queue_name.capitalize()
        state = self.collection_state.capitalize()
        filter = (": "+",".join(self.filter)) \
            if (self.filter != self.default_filter) else ""
        title = f"{queue} ({state}{filter})"
        checklist = Checklist()
        checklist.generate(title, tasks)
