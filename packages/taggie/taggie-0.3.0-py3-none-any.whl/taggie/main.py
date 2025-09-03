# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import argparse
import os
import sys
from importlib import import_module
from pathlib import Path

# from .taggers.files import Fnmatches, Extensions, Names
from typing import List, Optional, Set, Union

import msgspec

from ._version import __version__
from .reports.json_report import render_json_report
from .reports.table_report import render_table_report

PACKAGE_DIR = Path(__file__).parent.absolute()

DEFAULTS_DIR = PACKAGE_DIR / "defaults"

TAGGER_PACKAGE_DIRS = [PACKAGE_DIR / "taggers"]

TAGGER_PACKAGES = {
    path.stem.replace("_", "."): import_module(f".{path.stem}", "taggie.taggers")
    for tagger_package_dir in TAGGER_PACKAGE_DIRS
    for path in tagger_package_dir.glob("*.py")
    if not path.stem.startswith("_")
}

TAGGER_TYPES = [tagger.Tagger for tagger in TAGGER_PACKAGES.values()]


def register_taggers(tag_file: str, groups: Optional[List[str]] = None):
    if groups is None:
        groups = []

    taggers = msgspec.yaml.decode(
        open(tag_file).read(), type=List[Union[tuple(TAGGER_TYPES)]]
    )
    for tagger in taggers:
        if groups and not any(fi in tagger.groups for fi in groups):
            continue

        tagger_type = (
            Path(tagger.__class__.__module__)
            .suffix.lower()
            .replace(".", "")
            .replace("_", ".")
        )
        TAGGER_PACKAGES[tagger_type].register(tagger)


def get_tag_directory(tag_path: Path) -> Set[str]:
    tag_files = set()
    for root, _, files in os.walk(tag_path):
        root_path = Path(root)
        for file in files:
            if file.endswith(".yaml"):
                tag_files.add(str(root_path / file))
    return tag_files


def get_tag_files(tag_files: List[str]) -> Set[str]:
    all_tag_files = set()
    for tag_file in tag_files:
        tag_path = Path(tag_file)
        if tag_path.is_dir():
            all_tag_files |= get_tag_directory(tag_path)
        else:
            all_tag_files.add(tag_file)
    return all_tag_files


def get_all_files(path: Path) -> Set[str]:
    all_files = set()
    for root, _, files in os.walk(path):
        root_path = Path(root)
        relative_path = root_path.relative_to(path)
        for file in files:
            all_files.add(str(relative_path / file))
    return all_files


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--tag-file", dest="tag_files", action="append")
    parser.add_argument("-g", "--group", dest="groups", action="append")
    parser.add_argument(
        "-f",
        "--format",
        dest="output_format",
        choices=["json", "table"],
        default="table",
    )
    parser.add_argument("-o", "--output", dest="output_path", default="-")
    parser.add_argument(
        "-s", "--sort", dest="sort_by", choices=["most", "name"], default="most"
    )
    parser.add_argument("-e", "--exclude", action="append")
    parser.add_argument(
        "-V", "--version", action="version", version=f"taggie {__version__}"
    )
    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()

    if not args.tag_files:
        args.tag_files = [DEFAULTS_DIR.absolute()]

    base_path = Path.cwd()

    # print(TAGGER_PACKAGES)
    # print(TAGGER_TYPES)

    all_tag_files = get_tag_files(args.tag_files)
    # print(all_tag_files)

    all_files = get_all_files(base_path)

    if args.exclude:
        all_files = [
            file for file in all_files if not file.startswith(tuple(args.exclude))
        ]

    total_files = len(all_files)

    # total_files_after_exclusion = len(all_files)
    # print(all_files)

    # map_file_tags = {}
    # map_tag_files = {}

    for tag_file in all_tag_files:
        register_taggers(tag_file, groups=args.groups)

    all_found_tags = {}
    for tagger_type, tagger_package in TAGGER_PACKAGES.items():
        for tag, files in tagger_package.find_tags(all_files).items():
            all_found_tags.setdefault(tag, set())
            all_found_tags[tag] |= files

    metadata = dict(
        total_files=total_files,
    )

    output_file = sys.stdout if args.output_path == "-" else open(args.output_path, "w")

    if args.output_format == "json":
        output_file.write(
            render_json_report(metadata=metadata, found_tags=all_found_tags)
        )

    elif args.output_format == "table":
        output_file.write(
            render_table_report(
                metadata=metadata, found_tags=all_found_tags, sort_by=args.sort_by
            )
        )

    else:
        raise NotImplementedError(f"output format '{output_format}' not implemented")
