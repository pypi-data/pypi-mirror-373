# SPDX-FileCopyrightText: 2023 Helge
# SPDX-FileCopyrightText: 2024 Helge
#
# SPDX-License-Identifier: MIT

from fediverse_pasture_inputs.types import InputData
from fediverse_pasture_inputs.utils import format_as_json

mention_examples = [
    {
        "content": "basic mention; mention as list of dictionaries",
        "tag": [
            {
                "type": "Mention",
                "name": "@actor@test_server",
                "href": "http://pasture-one-actor/actor",
            }
        ],
    },
    {
        "content": "text @actor@pasture-one-actor; mention as dictionary",
        "tag": {
            "type": "Mention",
            "name": "@actor@test_server",
            "href": "http://pasture-one-actor/actor",
        },
    },
    {
        "content": "unrelated text",
        "tag": {
            "type": "Mention",
            "name": "something something",
            "href": "http://pasture-one-actor/actor",
        },
    },
    {
        "content": "Missing Name @actor@pasture-one-actor",
        "tag": {
            "type": "Mention",
            "href": "http://pasture-one-actor/actor",
        },
    },
    {
        "content": "text",
        "tag": {
            "type": "Mention",
            "name": "@the_milkman@mastodon.social",
            "href": "https://mastodon.social/users/the_milkman",
        },
    },
    {
        "content": "text",
        "tag": {
            "type": "Mention",
            "name": "@dummy@example",
            "href": "https://dummy.example",
        },
    },
    {
        "content": "text",
        "tag": {
            "type": "Mention",
            "name": "@test_actor@test_server",
            "href": "http://test_actor",
        },
    },
    {
        "content": "text",
        "tag": {
            "type": "as:Mention",
            "name": "yay",
            "href": "http://pasture-one-actor/actor",
        },
    },
    {
        "content": "@actor text",
        "tag": {
            "name": "@actor",
            "href": "http://pasture-one-actor/actor",
        },
    },
    {
        "content": "duplicate mention, see https://codeberg.org/funfedidev/fediverse-pasture-inputs/issues/75",
        "tag": [
            {
                "type": "Mention",
                "name": "@actor@test_server",
                "href": "http://pasture-one-actor/actor",
            },
            {
                "type": "Mention",
                "name": "@actor@test_server",
                "href": "http://pasture-one-actor/actor",
            },
        ],
    },
]


def mastodon_support(data):
    if not data:
        return "❌"
    if len(data.get("mentions", [])) > 0:
        return "✅ mention"
    return "parsed"


data = InputData(
    title="Mentions",
    frontmatter="""Mentions are discussed in [this section of
ActivityStreams](https://www.w3.org/TR/activitystreams-vocabulary/#microsyntaxes).

The big difference on if mentions are parsed are currently
a result of if the value in `href` can be resolved by the
application being tested.

In the support table `parsed` means that the activity could be parsed, but the mention was discarded.
A ❌ in the support table means that the entire message has failed to parse.
""",
    filename="mentions.md",
    examples=mention_examples,
    detail_table=True,
    detail_extractor={
        "activity": lambda x: format_as_json(x.get("object", {}).get("tag")),
        "mastodon": lambda x: format_as_json(x.get("mentions")),
        "firefish": lambda x: format_as_json(x.get("mentions")),
    },
    detail_title={
        "mastodon": "| tag | mentions | Example |",
        "firefish": "| tag | mentions | Example |",
    },
    support_table=True,
    support_title="tag",
    support_result={
        "activity": lambda x: format_as_json(
            x.get("object", {}).get("tag"), small=True
        )[0],
        "mastodon": mastodon_support,
        "firefish": mastodon_support,
    },
)
