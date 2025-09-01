from wizlib.parser import WizParser
from wizlib.ui.shell_ui import Emphasis

from busy.command import QueueCommand
from busy.model.item import Item
from busy.util import date_util


class AddCommand(QueueCommand):

    name = 'add'
    selection_optional = True
    pop: bool = False
    when: str = ""

    @classmethod
    def add_args(cls, parser: WizParser):
        # Special case, no filter argument
        parser.add_argument('--queue', '-q', default='tasks', nargs='?',
                            dest='queue_name')
        parser.add_argument('--pop', '-p', action='store_true', default=None)
        parser.add_argument('--when', '-w')
        parser.add_argument('markup', default="", nargs='?')

    def handle_vals(self):
        super().handle_vals()
        if not self.provided('markup'):
            self.markup = self.app.ui.get_text('Item: ')

    def check_when(self):
        plan_date = date_util.relative_date(self.when) if self.when else None
        if plan_date:
            return plan_date
        elif self.when:
            self.app.ui.send(f"Invalid time '{self.when}'", Emphasis.ERROR)
        return None

    @QueueCommand.wrap
    def execute(self):
        if self.markup:
            item = Item.from_markup(self.markup)
            self.queue.validate_tags(item.tags)
            # self.queue.validate_tags_active(item.tags)
            # self.validate_tags_active(item)
            # self.validate_tag_interdependencies([item])
            if self.provided('when'):
                plan_date = self.check_when()
                if plan_date:
                    plans = self.app.storage.get_collection(
                        self.queue_name, 'plan')
                    item.plan(plan_date)
                    plans.append(item)
                    self.set_next_item_status()
                    return
            if self.pop:
                self.collection.insert(0, item)
            else:
                self.collection.append(item)
        self.set_next_item_status()
