from __future__ import annotations
from dataclasses import dataclass, field
from functools import cached_property

from busy.error import BusyError


ACTIVE_LABEL = 'active'

TAGS_LABEL = 'tags'


class Configured:

    active: bool = True

    def set_active(self, config):
        """Set the active attribute based on the config. If the config itself
        is boolean, that's the active value, otherwise check the active
        attribute."""
        if isinstance(config, bool):
            self.active = config
        elif isinstance(config, dict) and ACTIVE_LABEL in config:
            self.active = config[ACTIVE_LABEL]
        else:
            self.active = True

    # def set_tags(self, config, queue):
    #     """Add a set of tags, and index them in the queue"""
    #     if isinstance(config, dict) and TAGS_LABEL in config:
    #         tags = {n:ConfiguredTag.from_config(n, c, tag) for
    # n,c in config[TAGS_LABEL]}


@dataclass
class ConfiguredQueue(Configured):

    name: str

    # The tags dictionary contains reference to all the configured tags
    configured_tags: dict[str, ConfiguredTag] = field(default_factory=dict)

    # Similar structure to tag.from_config - possible optimization opportunity?

    @classmethod
    def from_config(cls, name: str, config: dict | bool = None):
        queue = cls(name)
        queue.set_active(config)
        if isinstance(config, dict) and TAGS_LABEL in config:
            for tag_name in (tags_config := config[TAGS_LABEL]):
                ConfiguredTag.parse_config(
                    tag_name, tags_config[tag_name],
                    parent_or_queue=queue)
        return queue

    def add_tag(self, configured_tag):
        name = configured_tag.name
        if name in self.configured_tags:
            raise BusyError(
                f'Duplicate configured tag {name} in queue {self.name}')
        self.configured_tags[name] = configured_tag

    def get_tag(self, name):
        """Return the tag object for this queue if it exists - note that
        queue.tags is only the root level of the hierarchy"""
        return next(
            (x for t in self.configured_tags.values()
             if (x := t.get_tag(name))),
            None)

    def validate_is_active(self):
        if not self.active:
            raise BusyError(f"Queue {self.name} is inactive")

    def validate_tags(self, tags: set[str]):
        """Confirm that the tags passed in fit the hierarchy defined in the
        config (if any)"""
        if not isinstance(tags, set):
            tags = set(tags)
        for tag in tags:
            if configured_tag := self.get_tag(tag):
                if configured_tag.active is False:
                    raise BusyError(
                        f"Tag {tag} is inactive for queue {self.name}")
                if options := configured_tag.active_child_tags:
                    if len(tags & options) != 1:
                        raise BusyError(
                            f"Queue '{self.name}' requires items " +
                            f"with tag '{tag}' to have exactly one of " +
                            ' '.join(f"'{t}'" for t in sorted(options)))
                if (parent := configured_tag.parent):
                    if not ((name := parent.name) in tags):
                        raise BusyError(
                            f"Queue '{self.name}' requires items "
                            f"with tag '{tag}' to have parent tag '{name}'")

    # def validate_tags_active(self, tags):
    #     """Validate that all tags in the item are
    # active according to config"""
    #     for tag in tags:
    #         self._validate_active(self.tags_config, tag, "Tag")

    # def tag_violations_exist(self, tags:set[str]):
    #     """Given a set of tags, return true if there are hierarchy violations
    #     for this queue"""
    #     for tag in tags:
    #         if tag in self.parent2children:
    #             # Parent tag must have exactly one child
    #             children_present = tags.intersection(
    #                 self.parent2children[tag])
    #             if len(children_present) != 1:
    #                 return True
    #         if tag in self.child2parent:
    #             # Child tag must have its parent
    #             if self.child2parent[tag] not in tags:
    #                 return True
    #     return False

    # @cached_property
    # def parent2children(self):
    #     """A dict of tags, where values are the set of
    # children of that tag"""

    # def tag_is_actice(self, tag: str):


@dataclass
class ConfiguredTag(Configured):

    queue: ConfiguredQueue

    name: str

    parent: ConfiguredTag | None = field(default=None, kw_only=True)

    children: dict[str, ConfiguredTag] = field(
        default_factory=dict, kw_only=True)

    @classmethod
    def parse_config(cls, name: str, config: dict | bool = None, *,
                     parent_or_queue: ConfiguredTag | ConfiguredQueue):
        if isinstance(parent_or_queue, ConfiguredQueue):
            tag = cls(parent_or_queue, name)
        elif isinstance(parent_or_queue, ConfiguredTag):
            tag = cls(parent_or_queue.queue, name, parent=parent_or_queue)
        tag.set_active(config)
        if isinstance(config, dict) and TAGS_LABEL in config:
            for tag_name in (tags_config := config[TAGS_LABEL]):
                cls.parse_config(
                    tag_name, tags_config[tag_name],
                    parent_or_queue=tag)
        return tag

    def __post_init__(self):
        self.queue.add_tag(self)
        if self.parent:
            self.parent.add_child(self)

    def add_child(self, configured_tag):
        self.children[configured_tag.name] = configured_tag

    def get_tag(self, name):
        """Return self or descendent tag by name"""
        if name == self.name:
            return self
        else:
            return next(
                (x for t in self.children
                 if (x := self.children[t].get_tag(name))),
                None)

    @cached_property
    def active_child_tags(self) -> set:
        return set(t.name for t in self.children.values() if t.active)
