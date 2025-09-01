

from busy.command import CollectionCommand
from busy.util.edit import edit_items


class EditorCommandBase(CollectionCommand):

    selection_optional = True

    @CollectionCommand.wrap
    def execute(self):
        command = self.app.config.get('editor') or 'emacs'
        edit_items(self.collection,
                   self.selected_indices, command)
        self.validate_selection()

        # Check for tag interdependency warnings after editing
        # self.check_and_set_validation_warnings(self.set_next_item_status)
        self.set_next_item_status()


class EditOneItemCommand(EditorCommandBase):
    """Edit items; default to just one"""

    name = "edit"


class EditManyCommand(EditorCommandBase):
    """Edit items; default to all"""

    name = 'manage'
    default_filter = ["1-"]
