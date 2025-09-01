from . import Collection, SingleStateCollection


class PlanCollection(SingleStateCollection):

    state = 'plan'
    schema = ['plan_date', 'markup']
