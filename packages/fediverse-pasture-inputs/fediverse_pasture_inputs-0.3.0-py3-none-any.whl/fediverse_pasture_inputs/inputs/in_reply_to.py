# SPDX-FileCopyrightText: 2023 Helge
# SPDX-FileCopyrightText: 2024 Helge
#
# SPDX-License-Identifier: MIT

from fediverse_pasture_inputs.types import InputData, Details, Support
from fediverse_pasture_inputs.utils import format_as_json, safe_first_element


in_reply_to_examples = [
    {
        "content": "valid uri",
        "inReplyTo": "http://pasture-one-actor/assets/note1.jsonap",
    },
    {"content": "invalid uri", "inReplyTo": "http://invalid.example/"},
    {"content": "list", "inReplyTo": ["http://pasture-one-actor/assets/note1.jsonap"]},
    {
        "content": "Link in inReplyTo",
        "inReplyTo": {
            "type": "Link",
            "href": "http://pasture-one-actor/assets/note1.jsonap",
        },
    },
    {
        "content": "two elements in inReplyTo",
        "inReplyTo": [
            "http://pasture-one-actor/assets/note1.jsonap",
            "http://pasture-one-actor/assets/note2.jsonap",
        ],
    },
    {
        "content": "collection",
        "inReplyTo": {
            "type": "Collection",
            "items": ["http://pasture-one-actor/actor"],
        },
    },
    {
        "content": "embedded note",
        "inReplyTo": {
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": "Note",
            "id": "http://pasture-one-actor/assets/note1.jsonap",
            "to": ["as:Public"],
            "attributedTo": "http://pasture-one-actor/actor",
            "content": "One",
            "published": "2024-01-06T13:11:45Z",
        },
    },
]

details = Details(
    extractor={
        "activity": lambda x: format_as_json(x.get("object", {}).get("inReplyTo")),
        "mastodon": lambda x: format_as_json(x.get("in_reply_to_id"))
        + format_as_json(x.get("in_reply_to_account_id")),
        "firefish": lambda x: format_as_json(x.get("replyId"))
        + format_as_json(x.get("reply")),
    },
    title={
        "mastodon": "| inReplyTo | in_reply_to_id | in_reply_to_account_id | Ex. |",
        "firefish": "| inReplyTo | replyId | reply | Ex. |",
    },
)

support = Support(
    title="inReplyTo",
    result={
        "activity": lambda x: safe_first_element(
            format_as_json(x.get("object", {}).get("inReplyTo"))
        )
        or "",
        "mastodon": lambda x: "✅" if x else "❌",
        "firefish": lambda x: "✅" if x else "❌",
    },
)

data = InputData(
    title="Variations of inReplyTo",
    frontmatter="""
The property is defined [here](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-inreplyto). The
goal of this support table is to show how applications react to `inReplyTo` containing a wide variation
of allowed objects. As Fediverse applications generally only give one the option to reply to a single
element, the lacking support should not be surprising.
""",
    filename="in_reply_to.md",
    group="Object Properties",
    examples=in_reply_to_examples,
    details=details,
    support=support,
)
