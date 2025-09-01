from wizlib.parser import WizParser
from wizlib.command import CommandCancellation
from wizlib.ui.shell_ui import Emphasis

from busy.command import QueueCommand
from busy.error import BusyError
from busy.util import date_util


class Deferable(QueueCommand):

    @property
    def plan_date(self):
        return date_util.relative_date(self.when) \
            if self.when else None

    def ask_when(self):
        while True:
            self.when = self.app.ui.get_text(
                "When: ", [], (self.when or "tomorrow"))
            if self.check_when():
                break
        self.yes = True

    ask_when.name = 'other'
    ask_when.key = 'o'

    def check_when(self):
        if self.plan_date:
            return True
        else:
            self.app.ui.send(
                f"Invalid time '{self.when}'", Emphasis.ERROR)

    def get_default_when(self):
        items = self.selected_items
        if not self.provided('when'):
            # Timing not provided so start with the default
            repeats = set(i.repeat for i in items if i.repeat)
            if len(repeats) > 1:
                raise BusyError(
                    'Items have different repeat values')
            if repeats:
                self.when = next(iter(repeats))
                if not self.check_when():
                    self.ask_when()


class DeferCommand(Deferable):

    when: str = ""
    yes: bool = None
    name = 'defer'

    @classmethod
    def add_args(cls, parser: WizParser):
        super().add_args(parser)
        parser.add_argument('--when', '-w')
        cls.add_yes_arg(parser)

    def handle_vals(self):
        super().handle_vals()
        if self.selected_indices:
            self.app.ui.send(self.selected_items_list)
            self.get_default_when()
            if self.provided('when'):
                if not self.check_when():
                    self.ask_when()
            if not self.provided('yes'):
                if not self.when:
                    self.ask_when()
                if not self.provided('yes'):
                    intro = f"Defer {self.summarize()}"
                    intro += f" to {self.plan_date}"
                    self.confirm(intro, self.ask_when)

    @QueueCommand.wrap
    def execute(self):
        # self.validate_tag_interdependencies(self.selected_items)
        if not self.plan_date:
            raise BusyError('Invalid date')
        plans = self.app.storage.get_collection(self.queue_name, 'plan')
        items = self.collection.delete(self.selected_indices)
        for item in items:
            item.plan(self.plan_date)
        plans += items
        self.set_next_item_status()
