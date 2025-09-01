# Treat a collection as an in-memory database of Items, and this is the query
# engine.
#
# "Groups" create some degree of logic -- all the filters within a group are
# OR'd with each other, then groups are AND'ed against other groups.

import re

from busy.error import BusyError


class Selector:

    CRITERIUM_TYPES = []

    @classmethod
    def add_criterium_type(self, criterium_type):
        self.CRITERIUM_TYPES.append(criterium_type)

    def get_criterium(self, word):
        for criterium_type in self.CRITERIUM_TYPES:
            if criterium_type.match(word):
                if self.sequence_number_ok or not criterium_type.index:
                    return criterium_type(word)
        raise BusyError(f"Invalid selection criterium {word}")

    def __init__(self, args, sequence_number_ok=True):
        """Receives filters as arguments and initializes the selector. The
        sequence_number_ok parameter allows rejection of numeric (index-type)
        filters."""
        self.sequence_number_ok = sequence_number_ok
        result = {}
        for arg in args:
            criterium = self.get_criterium(arg)
            if hasattr(criterium, 'group'):
                groupnum = criterium.group
            else:
                # 9 arbitrarily high
                groupnum = max(max(result.keys() | [0]), 9) + 1
            if groupnum not in result:
                result[groupnum] = []
            result[groupnum].append(criterium)
        self.filter_groups = result

    def hit(self, index, value, count):
        """Return true if the value at the index matches the criteria logic"""
        for group in self.filter_groups:
            filters = self.filter_groups[group]
            hit = any(f.hit(index, value, count) for f in filters)
            if not hit:
                return False
        return True

    def indices(self, elements):
        """Return the indices of the elements that match the criteria"""
        enumeration = enumerate(elements)
        count = len(elements)
        return [i for i, t in enumeration if self.hit(i, t, count)]


class NumberCriterium:

    index = True
    group = 1

    def match(word):
        return str(word).isdigit()

    def __init__(self, word):
        self.index = int(word) - 1

    def hit(self, index, value, count):
        return index == self.index


Selector.add_criterium_type(NumberCriterium)


class RangeCriterium:

    index = True
    group = 1
    MATCH = r'^(\d+\-\d*)|\-$'

    @classmethod
    def match(cls, word):
        return isinstance(word, str) and bool(re.match(cls.MATCH, word))

    def __init__(self, word):
        split = word.split('-')
        self.start = int(split[0]) - 1 if split[0] else None
        self.end = int(split[1]) - 1 if split[1] else None

    def hit(self, index, value, count):
        if self.start is None and self.end is None:
            return index == count - 1
        elif self.end is None:
            return index >= self.start
        else:
            return index >= self.start and index <= self.end


Selector.add_criterium_type(RangeCriterium)


class TagCriterium:

    index = False
    group = 2

    def match(word):
        return isinstance(
            word, str) and bool(
            re.match(r'^[a-zA-Z][a-zA-Z0-9\-]*$', word))

    def __init__(self, word):
        self.tag = str(word).lower()

    def hit(self, index, value, count):
        return ('#' + self.tag) in str(value).lower().split()


Selector.add_criterium_type(TagCriterium)


class CombinedTagCriterium:

    index = False
    group = 2

    MATCH = r'^[a-zA-Z\-]+(\+[a-zA-Z\-]+)+$'
    FIND = r'([a-zA-Z\-]+)'

    @classmethod
    def match(cls, word):
        if isinstance(word, str):
            return bool(re.match(cls.MATCH, word))

    def __init__(self, word):
        tags = re.findall(self.FIND, word)
        self.tags = [t.lower() for t in tags]

    def hit(self, index, value, count):
        words = str(value).lower().split()
        return all(('#'+t in words) for t in self.tags)


Selector.add_criterium_type(CombinedTagCriterium)


class NamedCriterium:
    """If it contains a colon, it's more than a tag"""

    index = False

    def match(word):
        return isinstance(word, str) and \
            bool(re.match(r'^[a-z]+\:.+$', word))

    def __init__(self, arg: str):
        self.name, self.value = arg.split(':', maxsplit=1)

    def hit(self, index, value, count):
        try:
            method = getattr(value, 'filter_'+self.name)
        except AttributeError:
            raise BusyError(f'Unknown named filter {self.name}')
        return method(self.value)


Selector.add_criterium_type(NamedCriterium)


class FunctionCriterium:
    """Evaluates a function against the value (not the index) - not actualy
    used?"""

    index = False

    def match(arg):
        return callable(arg)

    def __init__(self, arg):
        self.func = arg

    def hit(self, index, value, count):
        return self.func(value)


Selector.add_criterium_type(FunctionCriterium)
