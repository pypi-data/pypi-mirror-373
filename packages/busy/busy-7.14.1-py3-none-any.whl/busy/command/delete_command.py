
from wizlib.parser import WizParser

from busy.command import CollectionCommand


class DeleteCommand(CollectionCommand):

    yes: bool = None
    name = 'delete'
    key = 'd'
    default_filter = [1]

    @classmethod
    def add_args(cls, parser: WizParser):
        super().add_args(parser)
        cls.add_yes_arg(parser)

    def handle_vals(self):
        super().handle_vals()
        if self.selected_indices:
            items = self.selected_items
            self.app.ui.send('\n'.join([str(i) for i in items]))
            self.confirm(f"Delete {self.summarize()}")

    # Assume the indices have been already set, before confirmation.

    @CollectionCommand.wrap
    def execute(self):
        deleted = self.collection.delete(self.selected_indices)
        self.set_next_item_status()
