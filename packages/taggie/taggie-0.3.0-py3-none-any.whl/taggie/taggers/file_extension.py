# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import re
from typing import Set

from msgspec import field

from ._base import _Tagger

# _EXTENSIONS = {}
_TAGS = {}


class Tagger(_Tagger, frozen=True, tag="file.extension"):
    extensions: Set[str] = field(default_factory=set)


def register(tagger: Tagger):
    # for tag in tagger.tags:
    #     _EXTENSIONS.setdefault(tag, set())
    #     _EXTENSIONS[tag] |= tagger.extensions

    for extension in tagger.extensions:
        _TAGS.setdefault(extension, set())
        _TAGS[extension] |= tagger.tags


# multi-line regex

# def find_tags(files: Set[str]) -> Set[str]:
#     pat_tokens = '|'.join('^(?P<%s>%s)$' % (extension, r".+\." + extension) for extension in _TAGS)
#     re_extensions = re.compile(pat_tokens, flags=re.MULTILINE)
#     tags_found = {}
#     for match in re_extensions.finditer('\n'.join(files)):
#         for tag in _TAGS[match.lastgroup]:
#             tags_found.setdefault(tag, set())
#             tags_found[tag].add(match.group())
#     return tags_found

# line-by-line regex


def find_tags(files: Set[str]) -> Set[str]:
    pat_tokens = "|".join(
        "^(?P<%s>%s)$" % (extension, r".+\." + extension) for extension in _TAGS
    )
    re_extensions = re.compile(pat_tokens)
    tags_found = {}
    for file in files:
        match = re_extensions.match(file)
        if match:
            for tag in _TAGS.get(match.lastgroup, set()):
                tags_found.setdefault(tag, set())
                tags_found[tag].add(match.group())
    return tags_found


# fnmatch filter

# def find_tags(files: Set[str]) -> Set[str]:
#     tags_found = {}
#     for extension in _TAGS:
#         files_found = set(fnmatch.filter(files, f"*.{extension}"))
#         if files_found:
#             for tag in _TAGS[extension]:
#                 tags_found.setdefault(tag, set())
#                 tags_found[tag] |= files_found
#     return tags_found

# match the extension

# def find_tags(files: Set[str]) -> Set[str]:
#     tags_found = {}
#     for file in files:
#         extension = Path(file).suffix.lower().replace(".", "")
#         if extension in _TAGS:
#             for tag in _TAGS[extension]:
#                 tags_found.setdefault(tag, set())
#                 tags_found[tag].add(file)

#     return tags_found
