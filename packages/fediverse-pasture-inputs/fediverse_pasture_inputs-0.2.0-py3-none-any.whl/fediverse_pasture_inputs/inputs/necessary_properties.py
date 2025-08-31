# SPDX-FileCopyrightText: 2023-2024 Helge
#
# SPDX-License-Identifier: MIT

from fediverse_pasture_inputs.types import InputData

examples = [
    {"content": "All fields"},
    {"content": "without id", "id": None},
    {"content": "without published", "published": None},
    {"content": "without attributedTo", "attributedTo": None},
    {"content": "without type", "type": None},
]

data = InputData(
    title="Necessary Properties",
    frontmatter="""With this support table, we want to illustrate, which properties
can be removed from an object, and still create an appropriate response. We note
that the basic form of an object is

```json
{
    "type": "Note",
    "attributedTo": "http://pasture-one-actor/actor",
    "to": [
      "as:Public",
      "http://mitra/users/admin"
    ],
    "id": "http://pasture-one-actor/actor/wFuWTn-8BiE",
    "published": "2023-11-28T11:38:15Z",
    "content": "All fields"
}
```
""",
    filename="necessary_properties.md",
    examples=examples,
    support_table=True,
    support_title="content",
    support_result={
        "activity": lambda x: x["object"]["content"] or "",
        "mastodon": lambda x: "✅" if x else "❌",
        "firefish": lambda x: "✅" if x else "❌",
    },
)
