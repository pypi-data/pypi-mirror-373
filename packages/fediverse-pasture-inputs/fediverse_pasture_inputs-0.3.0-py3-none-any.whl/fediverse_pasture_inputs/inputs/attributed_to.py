# SPDX-FileCopyrightText: 2024 Helge
#
# SPDX-License-Identifier: MIT

from fediverse_pasture_inputs.types import InputData, Details, Support
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

details = Details(
    title={
        "mastodon": "| attributedTo | account | Example |",
        "misskey": "| attributedTo | user | Example |",
    },
    extractor={
        "activity": lambda x: format_as_json(x.get("object", {}).get("attributedTo")),
        "mastodon": lambda x: format_as_json(x.get("account")),
        "misskey": lambda x: format_as_json(x.get("user")),
    },
)

support = Support(
    title="attributedTo",
    result={
        "activity": lambda x: format_as_json(
            x.get("object", {}).get("attributedTo"), small=True
        )[0],
        "mastodon": is_supported,
        "misskey": is_supported,
    },
)

data = InputData(
    title="Attribution Format",
    frontmatter="""
`attributedTo` is defined [here in the ActivityStreams Vocabulary](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-attributedto). It allows us to tell, who authored / owns the object.

This test explores what is allowed in the field.

""",
    filename="attributed_to.md",
    group="Object Properties",
    examples=attributed_to_examples,
    details=details,
    support=support,
)
