from . import Collection, SingleStateCollection


class DoneCollection(SingleStateCollection):

    state = 'done'
    schema = ['done_date', 'markup']
