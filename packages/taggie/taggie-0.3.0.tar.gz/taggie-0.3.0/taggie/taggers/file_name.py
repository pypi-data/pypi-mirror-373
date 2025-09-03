# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path
from typing import Set

from msgspec import field

from ._base import _Tagger

_TAGS = {}


class Tagger(_Tagger, frozen=True, tag="file.name"):
    names: Set[str] = field(default_factory=set)


def register(tagger: Tagger):
    for name in tagger.names:
        _TAGS.setdefault(name, set())
        _TAGS[name] |= tagger.tags


def find_tags(files: Set[str]) -> Set[str]:
    tags_found = {}
    for file in files:
        path = Path(file).name
        if path in _TAGS:
            for tag in _TAGS.get(path, set()):
                tags_found.setdefault(tag, set())
                tags_found[tag].add(path)
    return tags_found
