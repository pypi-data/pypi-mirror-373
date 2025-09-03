# Copyright 2025 fortune-python contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
from collections.abc import Sequence
from dataclasses import dataclass
from typing import IO, Self


@dataclass(frozen=True)
class Strfile:
    version: int
    numstr: int
    longlen: int
    shortlen: int
    flags: int
    delimeter: str
    positions: Sequence[int]

    @classmethod
    def read(cls, f: IO[bytes]) -> Self:
        return cls(
            version=int.from_bytes(f.read(4)),
            numstr=int.from_bytes(f.read(8)),
            longlen=int.from_bytes(f.read(8)),
            shortlen=int.from_bytes(f.read(8)),
            flags=int.from_bytes(f.read(8)),
            delimeter=f.read(8)[4:5].decode(),
            positions=read_bytes(f),
        )

    @classmethod
    def from_fortunes(cls, f: IO, delimiter: str = "%") -> Self:
        offsets = [0]
        max_len = 0
        min_len = 2 ** 32
        while (block := read_until_delim(f, delimiter)) != "":
            block_len = len(block)
            offsets.append(f.tell())
            max_len = max(max_len, block_len)
            min_len = min(min_len, block_len)
        return cls(
            version=1,
            numstr=len(offsets) - 1,
            longlen=max_len,
            shortlen=min_len,
            flags=0,
            delimeter=delimiter,
            positions=offsets,
        )

    def write(self, f: IO[bytes]) -> None:
        f.write(self.version.to_bytes(4))
        f.write(self.numstr.to_bytes(8))
        f.write(self.longlen.to_bytes(8))
        f.write(self.shortlen.to_bytes(8))
        f.write(self.flags.to_bytes(8))
        f.write((0).to_bytes(4) + self.delimeter.encode() + (0).to_bytes(3))
        for position in self.positions:
            f.write(position.to_bytes(8))


def read_bytes(f: IO[bytes]) -> list[int]:
    result = []
    while len(pos := f.read(8)) == 8:
        result.append(int.from_bytes(pos))
    return result


def read_until_delim(f: IO, delim: str, offset: int | None = None) -> str:
    if offset is not None:
        f.seek(offset)
    result = []
    pattern = rf"{re.escape(delim)}\n"
    while (line := f.readline()) != "" and not re.match(pattern, line):
        result.append(line)
    return "".join(result)
