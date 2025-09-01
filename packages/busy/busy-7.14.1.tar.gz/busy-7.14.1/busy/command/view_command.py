from functools import cached_property
import re
from types import SimpleNamespace

from jinja2.sandbox import SandboxedEnvironment

from busy.command import CollectionCommand, MultiCollectionCommand
from busy.error import BusyError
from busy.model.item import FORMATTABLE_FIELDS, Item

from wizlib.parser import WizParser

VALID_FIELDS = {'num'} | FORMATTABLE_FIELDS


class ViewCommand(MultiCollectionCommand):
    """View items from a queue. Default format is just the 'simple' field.
    """

    name = 'view'
    unique: bool = False

    @classmethod
    def add_args(cls, parser: WizParser):
        super().add_args(parser)
        formats = parser.add_mutually_exclusive_group()
        formats.add_argument(
            '--fixed', '-f', help='comma-separated fields to output')
        formats.add_argument(
            '--format', '-t', help='Python str.format template for each item')
        formats.add_argument(
            '--jinja', '-j', help='Jinja2 template for each item')
        formats.add_argument(
            '--list', '-i', action='store_true',
            help='List view with index numbers')
        parser.add_argument(
            '--unique', '-u', action='store_true',
            help='Performs a mildly fuzzy deduplication of output items')

    @CollectionCommand.wrap
    def execute(self):
        # Check for tag interdependency warnings
        # self.check_and_set_validation_warnings()

        if self.provided('jinja'):
            with open(self.jinja) as jinjafile:
                jinja = jinjafile.read()
                template = SandboxedEnvironment().from_string(jinja)
                items = [SimpleNamespace(**vals(m, x))
                         for x, m in self.viewable_items]
                return template.render(items=items)
        else:
            if self.provided('fixed'):
                row = self.fixed_format()
            elif self.provided('format'):
                row = self.format
            elif self.provided('list') and self.list:
                row = '{num:>6}  {listable}'
            else:
                row = '{base}'
            return '\n'.join(format_row(row, r, i) for i,
                             r in self.viewable_items)

    def fixed_format(self):
        """Format string for fixed width output"""
        cols = range(len(self.fields))
        formats = []
        for col in cols:
            field = self.fields[col]
            width = 1
            alignment = '<'
            for index, item in self.viewable_items:
                if field == 'num':
                    newwidth = len(str(index + 1))
                    alignment = '>'
                else:
                    # formattable = item.formattable
                    # if field in formattable and \
                    #         isinstance(formattable[field], int):
                    #     alignment = '>'
                    newwidth = colwidth(field, item)
                width = max(width, newwidth)
            formats += [f"{{{field}:{alignment}{width}}}"]
        return ' '.join(formats)

    @property
    def viewable_items(self):
        """Filter for uniqueness if requested"""
        if self.unique:
            items = []
            fuzzmatches = set()
            for index, item in reversed(self.selection):
                fuzzkey = item.fuzzkey
                if fuzzkey not in fuzzmatches:
                    items.append((index, item))
                    fuzzmatches.add(item.fuzzkey)
            items.reverse()
            return items
        else:
            return self.selection

    @property
    def fields(self):
        """Which fields are included in the output, validated - currently only
        works for fixed format."""
        fields = self.fixed.split(',')
        unknown_fields = [f for f in fields if
                          f.split('.')[0] not in VALID_FIELDS]
        if any(unknown_fields):
            raise BusyError(f"Unknown field(s) {','.join(unknown_fields)}")
        if 'num' in self.fixed and not self.collection.sequence_number_ok:
            raise BusyError('Invalid field num for multi-state view')
        return fields


def colwidth(field: str, item: Item) -> int:
    """Return the width required for a column, given the descriptor of a field
    and an item"""
    return len(('{' + field + '}').format(**item.formattable))


def vals(item: Item, index: int) -> dict:
    return item.formattable | {'num': index + 1}


def format_row(template: str, item: Item, index: int) -> str:
    return template.format(**vals(item, index)).rstrip()
