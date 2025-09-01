import re
from dataclasses import KW_ONLY, dataclass, field
from datetime import date, datetime
from typing import Optional


from busy.util.date_util import absolute_date
from busy.util.date_util import relative_date
from busy.util import date_util


class ItemStateError(Exception):
    pass


# Some handy constants

START_TIME_FORMAT = '%Y%m%d%H%M'
DATE_FORMAT = '%Y-%m-%d'
VALID_STATES = {'todo', 'plan', 'done'}

# Helpers for parsing - older versions of Busy supported an elaborate
# "followon" mechanism

FOLLOW_SPLIT = re.compile(r'\s*\-*\>\s*')
LEGACY_REPEAT = re.compile(r'^\s*repeat(?:\s+[io]n)?\s+(.+)\s*$', re.I)


# Dumb object to simplify format string use

class Obj:
    def __getattr__(self, attr):
        return ''


# Function to simplify joining strings

def _joined(*substrings, sep: str = ' '):
    return sep.join([s for s in substrings if s])


# Decorator to restrict operations to certain states

def restricted(*allowed_states):
    def wrapper(method):
        def replacement(self, *args, **kwargs):
            if self.state in allowed_states:
                return method(self, *args, **kwargs)
            else:
                raise ItemStateError(
                    f"Method not allowed in state '{self.state}'")
        return replacement
    return wrapper


@dataclass
class Item:
    """A single entry in a queue"""

    _: KW_ONLY

    # A unique identifier for the item
    id: str = None

    # The basic text of the item
    base: str

    # The state, which must be valid
    state: str = 'todo'

    # Unique tags, indicated by `#` in markup
    tags: set[str] = field(default_factory=set)

    # Data values, indicated by `%` and a single letter in markup
    vals: dict[str, str] = field(default_factory=dict)

    # A string describing if and when to repeat the item
    repeat: str = ''

    # A single URL, indicated by `@` in markup
    url: str = ''

    # Number of clock minutes spent on the task according to our crude timing
    # system
    elapsed_minutes: int = 0

    # Clock time that this task started, only for top item in `tasks` queue,
    # indicated by `!s` in markup
    start_time: Optional[datetime] = None

    # Date the item can be activated, only if item in `plan` state
    plan_date: Optional[date] = None

    # Date the item was done, only if item in `done` state
    done_date: Optional[date] = None

    @classmethod
    def from_markup(cls, markup: str, state: str = 'todo',
                    plan_date: date | str | None = None,
                    done_date: date | str | None = None):
        split = FOLLOW_SPLIT.split(markup, maxsplit=1)
        body = split[0] if split else ""

        if len(split) > 1:
            next = split[1]
            match = LEGACY_REPEAT.match(next)
            if match:
                repeat = match.group(1)
            else:
                repeat = next
        else:
            repeat = ""

        words = body.split()
        base = " ".join([w for w in words if w[0] not in '#@!%?'])
        def marked(mark): return [w[1:] for w in words if w.startswith(mark)]
        id = mid[0] if (mid := marked('?')) else ''
        tags = {m.lower() for m in marked('#')}
        url = murl[0] if (murl := marked('@')) else ''
        vals = {m[0]: m[1:] for m in marked('%')}
        timing_data = {m[0]: m[1:] for m in marked("!")}
        elapsed_minutes = int(timing_data['e']) if 'e' in timing_data else 0
        start_time = datetime.strptime(timing_data['s'], START_TIME_FORMAT) \
            if 's' in timing_data else None
        return cls(
            id=id,
            state=state,
            base=base,
            repeat=repeat,
            tags=tags,
            url=url,
            vals=vals,
            elapsed_minutes=elapsed_minutes,
            start_time=start_time,
            plan_date=absolute_date(plan_date),
            done_date=absolute_date(done_date)
        )

    # --- Limit state to valid options ---

    def __post_init__(self):
        if self.state not in VALID_STATES:
            raise ValueError(f"Item state must be one of {VALID_STATES}")

    # ---- Helpers to reconstruct markup ----

    @property
    def _mid(self):
        """The ID is marked with a questionmark, even though it's always
        first"""
        return f"?{self.id}" if self.id else ''

    @property
    def _mtags(self):
        return {f"#{t}" for t in self.tags}

    @property
    def _murl(self):
        return f"@{self.url}" if self.url else ''

    @property
    def _mvals(self):
        return {f"%{k}{v}" for k, v in self.vals.items()}

    @property
    def _melapsed(self):
        return f"!e{self.elapsed_minutes}" if self.elapsed_minutes else ''

    @property
    def _mstart(self):
        return f"!s{self.start_time.strftime(START_TIME_FORMAT)}" \
            if self.start_time else ''

    # ---- Output forms, including markup subcomponents ----

    @property
    def noparens(self):
        """Base text without parenthetical expressions"""
        result = ''
        depth = 0
        for char in self.base:
            if char == '(':
                depth += 1
            elif char == ')' and depth > 0:
                depth -= 1
            elif depth == 0:
                result += char
        return result.strip()

    @property
    def simple(self):
        """Base text plus marked tags"""
        return _joined(self.base, *self._mtags)

    @property
    def listable(self):
        """Simple plus repeat"""
        return _joined(self.simple, self.repeat, sep=' > ')

    @property
    def notiming(self):
        """Base text with tags, vals, and URL"""
        return _joined(self.simple, self._murl, *self._mvals)

    @property
    def body(self):
        """Everything except the repeat"""
        return _joined(self.notiming, self._melapsed, self._mstart)

    @property
    def checkbox(self):
        """GitLab-style Markdown checkbox"""
        checked = 'x' if self.state == 'done' else ' '
        return f"- [{checked}]"

    @property
    def fuzzkey(self):
        """Key for fuzzy matching and deduplication"""
        return self.noparens.lower()

    @property
    def markup(self):
        main = _joined(self._mid, self.body)
        return _joined(main, self.repeat, sep=' > ')

    def __str__(self):
        """Represent the item as its simple form"""
        return self.simple

    # ---- State operations ----

    @restricted('todo')
    def done(self, done_date: date, plan_date: date = None):
        """Updates the item to done and returns a copy as a plan for the
        plan_date if provided"""
        plan = None
        if plan_date:
            plan_props = {
                'state': 'plan',
                'plan_date': plan_date,
                'elapsed_minutes': None,
                'start_time': None
            }
            plan = Item(**(vars(self) | plan_props))
        self.state = 'done'
        self.done_date = done_date
        self.repeat = ''
        return plan

    @restricted('done')
    def undone(self):
        self.state = 'todo'

    @restricted('todo')
    def plan(self, plan_date: date):
        self.state = 'plan'
        self.plan_date = plan_date

    @restricted('plan')
    def unplan(self):
        self.state = 'todo'

    # ---- Timer operations ----

    @restricted('todo')
    def start_timer(self):
        """Starts timing when activity begins on a task - is really only ever
        called on the top todo task"""
        if self.base and not self.start_time:
            self.start_time = date_util.now()

    @restricted('todo')
    def stop_timer(self):
        """Stop the timer and update elapsed minutes, typically called before
        change operations"""
        if self.start_time:
            if self.base:
                now = date_util.now()
                prev_elapsed = self.elapsed_minutes
                new = (now - self.start_time).seconds // 60
                self.elapsed_minutes = new + prev_elapsed
            self.start_time = None

    # ---- Named filters for Selector ----

    def filter_val(self, key_val):
        val = self.vals[key_val[0]]
        return ((val is not None) and (val == key_val[1:]))

    def filter_donemin(self, min_date):
        if self.done_date:
            return self.done_date >= absolute_date(min_date)

    def filter_donemax(self, max_date):
        if self.done_date:
            return self.done_date <= absolute_date(max_date)

    def filter_planmin(self, min_date):
        if self.plan_date:
            return self.plan_date >= absolute_date(min_date)

    def filter_planmax(self, max_date):
        if self.plan_date:
            return self.plan_date <= absolute_date(max_date)

    # ---- Properties for reading in formatted output

    @property
    def _otags(self):
        """Object-like format for tags"""
        result = Obj()
        for tag in self.tags:
            setattr(result, tag, tag)
        return result

    @property
    def _ovals(self) -> Obj:
        """Object-like format for data vals"""
        result = Obj()
        for key in self.vals:
            setattr(result, key, self.vals[key])
        return result

    @property
    def _sdonedate(self) -> str:
        if self.state == 'done' and self.done_date:
            return self.done_date.strftime(DATE_FORMAT)

    @property
    def _splandate(self) -> str:
        if self.state == 'plan' and self.plan_date:
            return self.plan_date.strftime(DATE_FORMAT)

    @property
    def formattable(self):
        return {
            'tag': self._otags,
            'tags': ' '.join(self.tags),
            'val': self._ovals,
            'donedate': self._sdonedate,
            'plandate': self._splandate,
            'elapsed': str(self.elapsed_minutes)
        } | {k: getattr(self, k) for k in {'body', 'base', 'noparens',
                                           'simple', 'listable', 'id',
                                           'notiming', 'url', 'repeat',
                                           'markup', 'checkbox'}}


FORMATTABLE_FIELDS = {'id', 'body', 'base', 'noparens', 'simple', 'listable',
                      'notiming', 'url', 'repeat', 'markup', 'tags', 'tag',
                      'val', 'donedate', 'plandate', 'elapsed', 'checkbox'}
