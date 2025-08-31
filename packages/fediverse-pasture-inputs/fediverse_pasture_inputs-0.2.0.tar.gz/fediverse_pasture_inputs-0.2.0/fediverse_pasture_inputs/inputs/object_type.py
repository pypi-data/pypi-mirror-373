# SPDX-FileCopyrightText: 2023 Helge
# SPDX-FileCopyrightText: 2024 Helge
#
# SPDX-License-Identifier: MIT

import json

from fediverse_pasture_inputs.types import InputData
from fediverse_pasture_inputs.utils import pre_format


def format_type(type):
    """Formats the type for the table"""
    if isinstance(type, list):
        return "[" + ", ".join(type) + "]"
    return type


object_type_list = [
    "Article",
    "Audio",
    "Document",
    "Event",
    "Image",
    "Note",
    "Page",
    "Place",
    "Profile",
    "Relationship",
    "Tombstone",
    "Video",
    ["Note", "Article"],
    None,
]

data = InputData(
    title="Object types",
    frontmatter="""Varying the object type and investigation what happens
to the properties. Relevant properties are

```json
{
    "@context": "https://www.w3.org/ns/activitystreams",
    "type": "${type}",
    "name": "name",
    "summary": "summary",
    "content": "content"
}
```

where `type` is the property being varied between different entries in the
table. Object types are defined in 
[https://www.w3.org/TR/activitystreams-vocabulary/#object-types](https://www.w3.org/TR/activitystreams-vocabulary/#object-types).
""",
    details_frontmatter="""The [support table](#support-table) shows a ✅ if the object was parsed successfully,
so a blank space means that the object was discarded. In [details](#details), you find
how the fields `name`, `summary`, and `content` are being transformed by the
application's parser.
""",
    filename="object_types.md",
    examples=[
        {"type": obj_type, "name": "name", "summary": "summary", "content": "content"}
        for obj_type in object_type_list
    ],
    detail_table=True,
    detail_extractor={
        "activity": lambda x: pre_format(format_type(x.get("object", {}).get("type"))),
        "mastodon": lambda x: pre_format(x.get("content")),
        "mitra": lambda x: pre_format(x.get("content"), pre_wrap=True),
        "firefish": lambda x: pre_format(x.get("text")),
    },
    detail_title={
        "mastodon": "| type | content | Example |",
        "firefish": "| type | text | Example |",
    },
    support_table=True,
    support_title="type",
    support_result={
        "activity": lambda x: json.dumps(
            x.get("object", {}).get("type", "") if x else ""
        ),
        "mastodon": lambda x: "✅" if x else "",
        "firefish": lambda x: "✅" if x else "",
    },
)
