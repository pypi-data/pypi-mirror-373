# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import json
from typing import Any, Dict, Set


class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


def render_json_report(metadata: Any, found_tags: Dict[str, Set[str]]) -> str:
    return (
        json.dumps(
            {
                "metadata": metadata,
                "tags": {
                    key: {
                        "metadata": {
                            "total_files": len(value),
                            "total_files_pc": round(
                                (len(value) / metadata["total_files"]) * 100, 2
                            ),
                        },
                        "files": sorted(value),
                    }
                    for key, value in sorted(found_tags.items())
                },
            },
            indent=2,
            sort_keys=True,
            cls=SetEncoder,
        )
        + "\n"
    )
