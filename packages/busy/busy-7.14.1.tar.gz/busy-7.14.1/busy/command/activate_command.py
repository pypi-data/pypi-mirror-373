from wizlib.parser import WizParser

from busy.command import QueueCommand
from busy.util import date_util


def is_today_or_earlier(plan):
    return plan.plan_date <= date_util.today()


class ActivateCommand(QueueCommand):

    timing: str = ""
    yes: bool = None
    collection_state: str = 'plan'
    name = 'activate'
    default_filter = [is_today_or_earlier]
    selection_optional = True

    @classmethod
    def add_args(cls, parser: WizParser):
        super().add_args(parser)
        # parser.add_argument('--timing', '-t', default='today')
        cls.add_yes_arg(parser)

    def handle_vals(self):
        super().handle_vals()
        if self.selection:
            if not self.provided('yes'):
                self.app.ui.send(self.selected_items_list)
                intro = f"Activate {self.summarize()}"
                self.confirm(intro)

    @QueueCommand.wrap
    def execute(self):
        self.validate_selection()
        # self.validate_tag_interdependencies(self.selected_items)
        todos = self.app.storage.get_collection(self.queue_name)
        activated = self.collection.delete(self.selected_indices)
        for item in activated:
            item.state = 'todo'
        todos.extend(activated)
        self.set_next_item_status()
