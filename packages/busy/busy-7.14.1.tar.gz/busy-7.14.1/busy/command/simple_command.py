from busy.command import CollectionCommand

# Like base but with the tags


class SimpleCommand(CollectionCommand):

    name = "simple"

    @CollectionCommand.wrap
    def execute(self):
        # # Check for tag interdependency warnings
        # self.check_and_set_validation_warnings()

        return self.output_items(lambda i: i.simple)
