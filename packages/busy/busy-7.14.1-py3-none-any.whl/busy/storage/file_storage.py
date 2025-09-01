import os
import re
from dataclasses import dataclass
from io import IOBase
from pathlib import Path

from busy.model.collection import Collection
from busy.storage import Storage
from busy.util.identifier import Identifier

STATES = Collection.family_attrs('state')
RE_QUEUE = re.compile(f"([a-zA-Z0-9\\-]+)\\.({'|'.join(STATES)})\\.psv")


class FileStorage(Storage):

    def __init__(self, path: str, identifier: Identifier = None):
        self.directory = Path(path) if isinstance(path, str) else path
        self.directory.mkdir(parents=True, exist_ok=True)
        assert isinstance(self.directory, Path) and self.directory.is_dir()
        self.cache = {}
        self.identifier = identifier

    def filepath(self, queue: str, state: str) -> str:
        return self.directory / f"{queue}.{state}.psv"

    def get_collection(self, queue: str, state: str = 'todo'):
        cache_key = (queue, state)
        if cache_key not in self.cache:
            collection = Collection.family_member('state', state)()
            path = self.filepath(queue, state)
            if path.is_file():
                with open(path) as file:
                    collection.read_items(file, identifier=self.identifier,
                                          from_storage=True)
            self.cache[cache_key] = collection
        return self.cache[cache_key]

    def queue_exists(self, queue: str):
        collections = [self.get_collection(queue, s) for s in STATES]
        return any(len(c) for c in collections)

    @property
    def queue_names(self):
        """Return names of queues. Cache nothing."""
        result = set()
        for path in self.directory.iterdir():
            if path.is_file() and (match := RE_QUEUE.match(path.name)):
                queue = match.groups()[0]
                if (queue not in result) and path.stat().st_size:
                    result.add(queue)
        return result

    def save(self):
        """Save any changes and clear the cache"""
        while self.cache:
            key, collection = self.cache.popitem()
            if collection.changed:
                path = self.filepath(*key)
                with open(path, 'w') as file:
                    collection.write_items(file, identifier=self.identifier)
