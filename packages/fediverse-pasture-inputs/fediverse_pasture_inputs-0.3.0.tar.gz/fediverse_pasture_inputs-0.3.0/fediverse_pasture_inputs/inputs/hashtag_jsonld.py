# SPDX-FileCopyrightText: 2023 Helge
# SPDX-FileCopyrightText: 2024 Helge
#
# SPDX-License-Identifier: MIT

from fediverse_pasture_inputs.types import InputData

from .hashtags import details, support

hashtag_examples = [
    {
        "content": "text",
        "tag": {"type": "Hashtag", "name": "#test"},
    },
    {
        "content": "using as:Hashtag",
        "tag": {"type": "as:Hashtag", "name": "#test"},
    },
    {
        "content": "no type ⚠️ ",
        "tag": {"name": "#test"},
    },
    {
        "@context": "https://www.w3.org/ns/activitystreams",
        "content": "Hashtag not in @context ⚠️ ",
        "tag": {"type": "Hashtag", "name": "#test"},
    },
    {
        "@context": "https://www.w3.org/ns/activitystreams",
        "content": "Hashtag not in @context; as:Hashtag",
        "tag": {"type": "as:Hashtag", "name": "#test"},
    },
]

data = InputData(
    title="Hashtags and JSON-LD",
    frontmatter="""The examples here are various variations of creating
the Hashtag element in the tag list. These variations can be useful in
understanding how strict an application sees JSON-LD.

Hashtags are a good illustration of JSON-LD parsing as Hashtag is
not part of the ActivityStreams vocabulary.

All examples except the first are questionable, and probably should not
be used when publishing to the Fediverse. The examples marked with
⚠️ are expected to fail with a JSON-LD parser. The examples using
`as:Hashtag` are expected to fail with a JSON only parser.
""",
    filename="hashtag_jsonld.md",
    group="Technical Properties",
    examples=hashtag_examples,
    details=details,
    support=support,
)
