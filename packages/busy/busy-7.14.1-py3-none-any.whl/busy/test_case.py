# Handy test case helpers, in the main library for plugin developers

from datetime import date, datetime
from unittest.mock import Mock, patch
from wizlib.test_case import WizLibTestCase


class BusyTestCase(WizLibTestCase):

    @staticmethod
    def mock_storage(o, p, d=None):
        def gc(q, s='todo'):
            if s == 'todo':
                return o
            elif s == 'plan':
                return p
            elif s == 'done':
                return d
        s = Mock()
        s.get_collection.side_effect = gc
        return s

    @staticmethod
    def patchtime(*t):
        return patch('busy.util.date_util.now',
                     lambda: datetime(*t))

    @staticmethod
    def patchday(*d):
        return patch('busy.util.date_util.today',
                     lambda: date(*d))
