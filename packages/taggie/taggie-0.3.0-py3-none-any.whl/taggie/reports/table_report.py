# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

from typing import Any, Dict, Set

from tabulate import tabulate


def render_table_report(
    metadata: Any, found_tags: Dict[str, Set[str]], sort_by="most"
) -> str:
    table = []
    for tag, files in found_tags.items():
        table.append([len(files), tag, list(files)[0]])

    if sort_by == "most":
        table = sorted(table, key=lambda k: k[0], reverse=True)
    elif sort_by == "name":
        table = sorted(table, key=lambda k: k[1])
    else:
        raise NotImplementedError(f"can't sort by algorithm: {sort_by}")

    return (
        tabulate(
            table,
            tablefmt="plain",
            headers=["TOTAL", "NAME", "EXAMPLE"],
            colalign=["left", "left", "left"],
        )
        + "\n"
    )
