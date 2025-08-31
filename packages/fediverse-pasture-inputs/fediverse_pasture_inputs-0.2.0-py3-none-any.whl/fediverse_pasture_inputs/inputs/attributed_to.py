# SPDX-FileCopyrightText: 2024 Helge
#
# SPDX-License-Identifier: MIT

from fediverse_pasture_inputs.types import InputData
from fediverse_pasture_inputs.utils import format_as_json, is_supported

attributed_to_examples = [
    {"attributedTo": "http://pasture-one-actor/actor", "content": "single element"},
    {
        "attributedTo": ["http://pasture-one-actor/actor"],
        "content": "single element as list",
    },
    {
        "attributedTo": [
            "http://pasture-one-actor/actor",
            "http://pasture-one-actor/second",
        ],
        "content": "two elements as list",
    },
    {
        "attributedTo": {"type": "Person", "id": "http://pasture-one-actor/actor"},
        "content": "a dictionary",
    },
    {
        "attributedTo": [{"type": "Person", "id": "http://pasture-one-actor/actor"}],
        "content": "a dictionary",
    },
]


data = InputData(
    title="Attribution Format",
    frontmatter="""
`attributedTo` is defined [here in the ActivityStreams Vocabulary](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-attributedto). It allows us to tell, who authored / owns the object.

This test explores what is allowed in the field.

""",
    filename="attributed_to.md",
    examples=attributed_to_examples,
    detail_table=True,
    detail_extractor={
        "activity": lambda x: format_as_json(x.get("object", {}).get("attributedTo")),
        "mastodon": lambda x: format_as_json(x.get("account")),
        "firefish": lambda x: format_as_json(x.get("user")),
    },
    detail_title={
        "mastodon": "| attributedTo | account | Example |",
        "firefish": "| attributedTo | user | Example |",
    },
    support_table=True,
    support_title="attributedTo",
    support_result={
        "activity": lambda x: format_as_json(
            x.get("object", {}).get("attributedTo"), small=True
        )[0],
        "mastodon": is_supported,
        "firefish": is_supported,
    },
)
