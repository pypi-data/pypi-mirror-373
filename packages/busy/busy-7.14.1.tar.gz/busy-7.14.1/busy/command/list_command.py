# We're slowly deprecating this command in favour of the view command

from wizlib.parser import WizParser

from busy.command import CollectionCommand
from busy.util.date_util import absolute_date


class ListCommand(CollectionCommand):
    """Show the markup with selection numbers, default to all. Includes summary
    output."""

    name = 'list'
    default_filter = ['1-']
    FORMATS = {
        'markup': "{!s}",
        'plan_date': "{:%Y-%m-%d}",
        'done_date': "{:%Y-%m-%d}"
    }

    def handle_vals(self):
        super().handle_vals()
        self.named_filters = []
        if self.provided('done_min'):
            def minfunc(i): return i.done_date >= absolute_date(self.done_min)
            self.named_filters.append(minfunc)
        if self.provided('done_max'):
            def maxfunc(i): return i.done_date <= absolute_date(self.done_max)
            self.named_filters.append(maxfunc)

    @CollectionCommand.wrap
    def execute(self):
        def format(item, index):
            result = f"{(index+1):>6}"
            for colname in self.collection.schema:
                format = self.FORMATS[colname]
                if (colname == 'markup'):
                    value = item.listable
                else:
                    value = getattr(item, colname)
                result += f"  {format.format(value)}"
            return result

        # Check for tag interdependency warnings
        # self.check_and_set_validation_warnings(
        #     lambda: setattr(self, 'status', self.summarize()))
        self.status = self.summarize()

        return self.output_items(format, with_index=True)
