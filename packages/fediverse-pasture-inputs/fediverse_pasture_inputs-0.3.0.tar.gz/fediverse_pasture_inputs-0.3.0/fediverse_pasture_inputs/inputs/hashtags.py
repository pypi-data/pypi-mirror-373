# SPDX-FileCopyrightText: 2023 Helge
# SPDX-FileCopyrightText: 2024 Helge
#
# SPDX-License-Identifier: MIT

from fediverse_pasture_inputs.types import InputData, Details, Support
from fediverse_pasture_inputs.utils import format_as_json

hashtag_examples = [
    {
        "content": "text",
        "tag": {"type": "Hashtag", "name": "#test"},
    },
    {
        "content": "text",
        "tag": {"type": "Hashtag", "name": "nohash"},
    },
    {
        "content": "text",
        "tag": {"type": "Hashtag", "name": "#with-dash_under"},
    },
    {
        "content": "text",
        "tag": {"type": "Hashtag", "name": "#with white space"},
    },
    {
        "content": "text",
        "tag": {"type": "Hashtag", "name": "#with(subtag)"},
    },
    {
        "content": "text",
        "tag": {"type": "Hashtag", "name": "#with123"},
    },
    {
        "content": "text",
        "tag": {"type": "Hashtag", "name": "#1234"},
    },
    {
        "content": "text",
        "tag": {"type": "Hashtag", "name": "#CamelCase"},
    },
    {
        "content": "text",
        "tag": {"type": "Hashtag", "name": "#ümläütß"},
    },
    {
        "content": "text",
        "tag": {"type": "Hashtag", "name": "#🐄"},
    },
    {
        "content": "text",
        "tag": {"type": "Hashtag", "name": "#❤️"},
    },
    {
        "content": "text",
        "tag": {"type": "Hashtag", "name": "#牛"},
    },
    {
        "content": "broken url parameter",
        "tag": {
            "type": "Hashtag",
            "name": "#test",
            "url": "https://ignore.example",
        },
    },
]


def mastodon_hashtag(x):
    if not x:
        return ""
    tags = x.get("tags", [])
    if len(tags) == 0:
        return ""
    return tags[0]["name"]


def misskey_hashtag(x):
    if not x:
        return ""
    tags = x.get("tags", [])
    if len(tags) == 0:
        return ""
    return tags[0]


def activity_for_support(x):
    obj = x["object"]

    tag_text = obj["tag"].get("name", "")

    if obj["content"] != "text":
        return f"""{tag_text}<br>{obj["content"]}"""

    return tag_text


details = Details(
    extractor={
        "activity": lambda x: format_as_json(x.get("object", {}).get("tag")),
        "mastodon": lambda x: format_as_json(x.get("tags")),
        "misskey": lambda x: format_as_json(x.get("tags")),
    },
    title={
        "mastodon": "| tag | tags | Example |",
        "misskey": "| tag | tags | Example |",
    },
)

support = Support(
    title="tag",
    result={
        "activity": activity_for_support,
        "mastodon": mastodon_hashtag,
        "misskey": misskey_hashtag,
    },
)

data = InputData(
    title="Hashtags",
    frontmatter="""The following mostly illustrates how the
name of a hashtag gets transformed by the applications. The input has the form

```json
"tag": {"type": "Hashtag", "name": "${tag}"}
```

The last two examples illustrate more technical behavior. For particularities
in parsing see [Hashtags and JSON-LD](./hashtag_jsonld.md).
""",
    filename="hashtags.md",
    group="Object Content",
    examples=hashtag_examples,
    details=details,
    support=support,
)
