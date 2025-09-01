from busy.command import CollectionCommand


class DescribeCommand(CollectionCommand):
    """Show the full markup"""

    name = 'describe'

    @CollectionCommand.wrap
    def execute(self):
        # Check for tag interdependency warnings
        # self.check_and_set_validation_warnings()

        return self.output_items(lambda i: i.markup)
