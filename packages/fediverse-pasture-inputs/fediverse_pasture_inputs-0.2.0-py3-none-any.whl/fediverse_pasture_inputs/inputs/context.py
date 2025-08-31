# SPDX-FileCopyrightText: 2023 Helge
# SPDX-FileCopyrightText: 2024 Helge
#
# SPDX-License-Identifier: MIT

from fediverse_pasture_inputs.types import InputData
from fediverse_pasture_inputs.utils import format_as_json

examples = [
    {
        "@context": "https://www.w3.org/ns/activitystreams",
        "content": "@context url as the ActivityStreams URL",
    },
    {
        "@context": ["https://www.w3.org/ns/activitystreams"],
        "content": "@context url is list of ActivityStreams URL",
    },
    {
        "@context": [
            "https://www.w3.org/ns/activitystreams",
            {"Hashtag": "as:Hashtag"},
        ],
        "content": "@context url is list of ActivityStreams URL and Hashtag",
    },
    {
        "@context": [
            "https://www.w3.org/ns/activitystreams",
            "https://w3id.org/fep/5711",
        ],
        "content": "@context with ActivityStreams URL + w3id-fep document",
    },
    {
        "@context": None,
        "content": "no @context",
    },
    {
        "@context": "http://strange.example/context",
        "content": "@context is a broken url",
    },
]

data = InputData(
    title="JSON-LD @context",
    frontmatter="""
Various examples the `@context` property can take.
See [here](https://www.w3.org/TR/json-ld11/#the-context) for the
W3C specification, and [here](https://www.w3.org/TR/activitystreams-core/#jsonld)
for what ActivityStreams says about it.
""",
    filename="context.md",
    examples=examples,
    detail_table=True,
    detail_extractor={
        "activity": lambda x: format_as_json(x),
        "mastodon": lambda x: format_as_json(x),
        "misskey": lambda x: format_as_json(x),
    },
    detail_title={
        "mastodon": "| activity | result | Ex. |",
        "misskey": "| activity | result | Ex. |",
    },
    support_table=False,
)
