from busy.command import BusyCommand


class QueuesCommand(BusyCommand):

    name = 'queues'

    @BusyCommand.wrap
    def execute(self):
        """Get the names of the queues. Cache nothing."""
        names = sorted(self.app.storage.queue_names)
        return '\n'.join(names)
