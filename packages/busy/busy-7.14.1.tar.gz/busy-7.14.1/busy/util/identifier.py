import os
import fcntl
import time
from pathlib import Path


# Utility to manage unique item identifiers that can be used to enable
# multi-device use and data merging.
#
# The scope of the identifiers includes:
#
# - **domain** included in configuration (and not actually implemented) with
#   the idea that a domain is a single user in a single context, and that
#   merges can only happen between addresses on the same domain. So the domain
#   is the namespace for identifiers.
# - **address* really just a device identifier, though could be used for
#   multiple addresses on one device (for example, to hold personal and work
#   data sets). Also stored in the configuration. There are up to 32 addresses
#   within a domain. Addresses are shown in all identifiers as the first
#   character of the identifier. For example, if the identifier is 'B64JW9'
#   then the address is 'B'.
# - **counter** a 5-character base-32 counter than is incremented each time a
#   new identifier is needed. The latest counter value is stored alongside the
#   data files.

BASE32_ALPHABET = '0123456789ABCDEFGHJKLMNPQRSTUVWX'
COUNTER_WIDTH = 5
COUNTER_FILENAME = 'counter'
COUNTER_START = '00000'


class Identifier:
    def __init__(self, address: str, directory: str, width=COUNTER_WIDTH):
        self.width = width
        if address not in BASE32_ALPHABET:
            raise ValueError(
                f"Invalid device address {address}"
            )
        self.address = address
        self.file = Path(directory) / COUNTER_FILENAME
        if not self.file.exists():
            self.file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.file, 'w') as f:
                f.write(COUNTER_START)

    def _encode(self, number: int) -> str:
        """Convert integer to fixed-width base32 string"""
        if number >= (32 ** self.width):
            raise ValueError(
                f"Value {number} exceeds {self.width} characters")
        result = ''
        for _ in range(self.width):
            result = BASE32_ALPHABET[number % 32] + result
            number //= 32
        return result

    def _decode(self, base32: str) -> int:
        """Convert base32 string to integer"""
        if len(base32) != self.width:
            raise ValueError(
                f"Identifiers must have {self.width} characters"
            )
        result = 0
        for char in base32:
            if char not in BASE32_ALPHABET:
                raise ValueError(f"Invalid base32 character: {char}")
            result = result * 32 + BASE32_ALPHABET.index(char)
        return result

    def increment(self):
        """Read current identifier, increment counter, and return new
        identifier"""
        with open(self.file, 'r+') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.seek(0)
                prev = f.read().strip()
                if not prev:
                    raise RuntimeError(f'Data missing from {self.file}')
                next = self._encode(self._decode(prev) + 1)
                f.seek(0)
                f.write(next)
                f.truncate()
                f.flush()
                os.fsync(f.fileno())  # Force write to disk
                return f"{self.address}{next}"
            finally:
                pass
