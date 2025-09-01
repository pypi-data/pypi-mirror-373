from datetime import datetime
from functools import cached_property
from importlib import import_module

from wizlib.command import WizCommand
from wizlib.parser import WizParser
from wizlib.ui import Choice, Chooser
from wizlib.command import CommandCancellation

from busy.model.collection import Collection
from busy.error import BusyError
from busy.model.configured import ConfiguredQueue


class BusyCommand(WizCommand):

    default = 'simple'

    # TODO: Move to wizlib
    @staticmethod
    def add_yes_arg(parser: WizParser):
        parser.add_argument('--yes', '-y', action='store_true', default=None)

    # TODO: Move to wizlib
    def confirm(self, verb, *other_actions):
        """Ensure that a command is confirmed by the user"""
        if self.provided('yes'):
            return self.yes
        else:
            def cancel():
                raise CommandCancellation('Cancelled')
            chooser = Chooser(f"{verb}?", 'OK', [
                Choice('OK', '\n', True),
                Choice('cancel', 'c', cancel)
            ])
            for action in other_actions:
                name = action.name if hasattr(action, 'name') else 'other'
                key = action.key if hasattr(action, 'key') else 'o'
                chooser.add_choice(name, key, action)
            choice = self.app.ui.get_option(chooser)
            if type(choice) is bool:
                self.yes = choice
            return choice


class QueueCommand(BusyCommand):
    """Base for commands that work on the default collection of one queue"""

    queue_name: str = 'tasks'
    collection_state: str = 'todo'
    filter: list = None
    default_filter = [1]
    named_filters: list = []
    selection_optional = False

    @property
    def collection(self):
        """Return the collection object being queried, usually todo"""
        if not hasattr(self, '_collection'):
            self._collection = self.app.storage.get_collection(
                self.queue_name, self.collection_state)
        return self._collection

    @property
    def complete_filter(self):
        """Simple filters plus named filters"""
        return self.filter + self.named_filters

    @property
    def selection(self):
        """Pairs (index, item) selected by filter"""
        return self.collection.selection(
            *self.complete_filter)

    @property
    def selected_indices(self):
        """Indices selected by filter"""
        return [i for i, t in self.selection]

    @property
    def selected_items(self):
        """Items in the selection"""
        return [t for i, t in self.selection]

    @property
    def selected_items_list(self):
        """Simple text list of selected items"""
        return '\n'.join([i.listable for i in self.selected_items])

    def time_value(self, minutes):
        """Estimated value of effort, usable for billable hours, rounded to one
        decimal place"""
        if not hasattr(self, '_multiplier'):
            self._multiplier = self.app.config.get('busy-multiplier') or 1.0
        adjusted_minutes = int(self._multiplier * minutes)
        return f"{adjusted_minutes//60}h{adjusted_minutes%60}m"

    def summarize(self, items: list = None):
        if items is None:
            items = self.selected_items
        if len(items) == 1:
            result = "1 item"
        elif len(items) > 1:
            result = str(len(items)) + " items"
        else:
            return "nothing"
        elapsed = sum(i.elapsed_minutes for i in items)
        if elapsed:
            result += f" ({self.time_value(elapsed)})"
        return result

    @classmethod
    def add_args(cls, parser: WizParser):
        super().add_args(parser)
        parser.add_argument('--queue', '-q', default='tasks', nargs='?',
                            dest='queue_name')
        parser.add_argument('filter', nargs="*")

    @cached_property
    def queue(self):
        """The object holding the Queue configuration including tag
        configuration"""
        return self.app.get_queue(self.queue_name)

    def validate_selection(self):
        for item in self.selected_items:
            self.queue.validate_tags(item.tags)

    # @cached_property
    # def queues_config(self):
    #     """Get the queues configuration from app config"""
    #     return self.app.config.get('busy-queues')

    # @cached_property
    # def queue_config(self):
    #     """Get the configuration setting for the current queue"""
    #     return self.queue.config
    #     # return self.queues_config.get(
    #     #     self.queue_name) if self.queues_config else None

    # @cached_property
    # def tags_config(self):
    #     """Get the tags configuration for the current queue"""
    #     if not self.queue_config or isinstance(self.queue_config, bool):
    #         return None
    #     tags_config = self.queue_config.get('tags')
    #     if tags_config:
    #         self._validate_unique_tag_definitions(tags_config)
    #     return tags_config

    # @cached_property
    # def tag_hierarchy(self):
    #     """Get the parent-child relationships for tags in the
    # current queue"""
    #     if not self.tags_config:
    #         return {}, {}
    #     return self._build_tag_hierarchy(self.tags_config)

    # def _validate_unique_tag_definitions(self, tags_config):
    #     """Validate that tags are not defined in multiple places within the
    #     queue"""
    #     all_tags = set()

    #     def collect_tags(config_dict):
    #         if not isinstance(config_dict, dict):
    #             return

    #         for tag_name, tag_config in config_dict.items():
    #             if tag_name in all_tags:
    #                 raise BusyError(
    #                     f"Duplicate tag definition: '{tag_name}' is " +
    #                     f"defined in multiple places within the queue")
    #             all_tags.add(tag_name)

    #             # Process nested tags
    #             if isinstance(tag_config, dict) and 'tags' in tag_config:
    #                 collect_tags(tag_config['tags'])

    #     collect_tags(tags_config)

    # def _is_active(self, setting):
    #     """Helper method to determine if a setting indicates active status"""
    #     if isinstance(setting, bool):
    #         return setting
    #     elif isinstance(setting, dict):
    #         return setting.get('active', True)
    #     else:
    #         return True  # Default to active for any other value or None

    # def _validate_active(self, config_dict, item_name, item_type):
    #     """Validate that an item is active according to config"""
    #     if not config_dict:
    #         return  # No config means allow all

    #     # Check direct setting first, then catchall
    #     setting = config_dict.get(item_name)
    #     if setting is None:
    #         setting = config_dict.get('_')

    #     if setting is not None and not self._is_active(setting):
    #         raise BusyError(f"{item_type} '{item_name}' is inactive")

    # def validate_queue_active(self):
    #     """Validate that the current queue is active according to config"""
    #     if not self.queue.is_active:
    #         raise BusyError(f"Inactive queue {self.queue_name}")
    #     # self._validate_active(self.queues_config, self.queue_name, "Queue")

    def validate_tags_active(self, item):
        """Validate that all tags in the item are active according to config"""
        for tag in item.tags:
            self._validate_active(self.tags_config, tag, "Tag")

    # def _build_tag_hierarchy(self, tags_config):
    #     """Build a mapping of parent-child relationships from tags config"""
    #     parent_to_children = {}
    #     child_to_parent = {}

    #     def process_level(config_dict, parent=None):
    #         if not isinstance(config_dict, dict):
    #             return

    #         for tag_name, tag_config in config_dict.items():
    #             if parent is not None:
    #                 # This is a child tag
    #                 if parent not in parent_to_children:
    #                     parent_to_children[parent] = set()
    #                 parent_to_children[parent].add(tag_name)
    #                 child_to_parent[tag_name] = parent

    #             # Process nested tags
    #             if isinstance(tag_config, dict) and 'tags' in tag_config:
    #                 process_level(tag_config['tags'], tag_name)

    #     if tags_config:
    #         process_level(tags_config)

    #     return parent_to_children, child_to_parent

    # def validate_tag_interdependencies(self, items, raise_exception=True):
    #     """Validate tag interdependency rules for items"""
    #     if not self.tags_config:
    #         return None  # No hierarchy configured

    #     parent_to_children, child_to_parent = self.tag_hierarchy

    #     invalid_items = [
    #         item for item in items
    #         if self._item_has_tag_violations(
    #             item, parent_to_children, child_to_parent)]

    #     if invalid_items:
    #         violation_text = '\n'.join(item.listable for
    # item in invalid_items)
    #         message = f"One or more items have tag interdependency " + \
    #             f"validation violations:\n{violation_text}"

    #         if raise_exception:
    #             raise BusyError(message)
    #         else:
    #             return message

    #     return None

    # def _item_has_tag_violations(
    #         self, item, parent_to_children, child_to_parent):
    #     """Check if an item has tag interdependency violations"""
    #     for tag in item.tags:
    #         if tag in parent_to_children:
    #             # Parent tag must have exactly one child
    #             children_present = item.tags.intersection(
    #                 parent_to_children[tag])
    #             if len(children_present) != 1:
    #                 return True

    #         if tag in child_to_parent:
    #             # Child tag must have its parent
    #             if child_to_parent[tag] not in item.tags:
    #                 return True

    #     return False

    # def check_and_set_validation_warnings(self, fallback_status_method=None):
    #     """Helper method to check for tag interdependency warnings and set
    #     status appropriately"""
    #     warning = self.validate_tag_interdependencies(
    #         self.selected_items, raise_exception=False)
    #     if warning:
    #         self.status = warning
    #     elif fallback_status_method:
    #         fallback_status_method()

    def handle_vals(self):
        """Apply default filter and stop the timer"""
        super().handle_vals()
        self.queue.validate_is_active()
        # self.validate_queue_active()
        if not self.provided('filter'):
            self.filter = self.default_filter
        if self.selection_optional or self.selected_indices:
            self.stop_current_task_timer()

    # We use a crude system for measuring elapsed time, which involves setting
    # the start_time and elapased_minutes values on the first item in the tasks
    # queue

    def stop_current_task_timer(self):
        """Stop the timer on the current top task before performing an
        operation, if we're working with the tasks queue"""
        if self.queue_name == 'tasks':
            todos = self.app.storage.get_collection('tasks', 'todo')
            if len(todos) > 0:
                todos[0].stop_timer()
                todos.changed = True

    def start_current_task_timer(self):
        """Start the timer on the current top task after performing an
        operation, if we're working with the tasks queue"""
        if self.queue_name == 'tasks':
            todos = self.app.storage.get_collection('tasks', 'todo')
            if len(todos) > 0:
                todos[0].start_timer()
                todos.changed = True

    @BusyCommand.wrap
    def execute(self, method, *args, **kwargs):
        """Handle timing and save operation"""
        result = None
        if self.selection_optional or self.selected_indices:
            result = method(self, *args, **kwargs)
            self.start_current_task_timer()
            self.app.storage.save()
        return result

    def set_next_item_status(self):
        """Sets the status to the top item in the todo collection of this
        command's queue for convenient output"""
        todos = self.app.storage.get_collection(self.queue_name, 'todo')
        self.status = todos[0].simple if len(todos) else None

    def output_items(self, func, with_index=False):
        """Return some attribute of all the items in the collection"""
        if with_index:
            return '\n'.join(func(self.collection[i], i)
                             for i in self.selected_indices)
        else:
            return '\n'.join(func(i) for i in self.selected_items)


class CollectionCommand(QueueCommand):
    """Base for commands that work on a user-specified collection"""

    states = ['done', 'todo', 'plan']

    @classmethod
    def add_args(cls, parser: WizParser):
        super().add_args(parser)
        parser.add_argument(
            '--state', '-s', action='store', default='todo',
            dest='collection_state', choices=cls.states)


class MultiCollectionCommand(CollectionCommand):
    """Base for commands that work on an optional user-specified collection. If
    no collection is specified, then numeric filters don't work and the command
    must be read-only."""

    states = ['done', 'todo', 'plan', 'multi']
    default_filter = []

    @property
    def collection(self):
        """Return the collection object being queried, which could include
        multiple states"""
        if self.collection_state == 'multi':
            if not hasattr(self, '_collection'):
                self._collection = Collection()
                for state in self.states[:-1]:
                    collection = self.app.storage.get_collection(
                        self.queue_name, state)
                    if collection:
                        self._collection += [i for i in collection]
            return self._collection
        else:
            return super().collection


class NullCommand(QueueCommand):
    name = 'null'

    @QueueCommand.wrap
    def execute(self):
        pass


class IntegrationCommand:

    def execute_integration(self):
        module = import_module('busy_' + self.integration)
        integration = module.Main()
        func = getattr(integration, self.name)
        result = func(self)
        return result
