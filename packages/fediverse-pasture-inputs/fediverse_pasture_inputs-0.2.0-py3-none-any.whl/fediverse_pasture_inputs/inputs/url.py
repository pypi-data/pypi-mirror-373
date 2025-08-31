# SPDX-FileCopyrightText: 2023 Helge
# SPDX-FileCopyrightText: 2024 Helge
#
# SPDX-License-Identifier: MIT

from fediverse_pasture_inputs.types import InputData
from fediverse_pasture_inputs.utils import pre_format, escape_markdown, format_as_json

link_html = {
    "type": "Link",
    "mediaType": "text/html",
    "href": "http://html.example/objects/123",
}

link_video = {
    "type": "Link",
    "mediaType": "video/mp4",
    "href": "http://video.example/objects/123",
}


url_examples = [
    "http://remote.example/objects/123",
    ["http://remote.example/objects/123"],
    ["http://remote.example/objects/123", "http://other.example/objects/123"],
    ["http://other.example/objects/123", "http://remote.example/objects/123"],
    link_html,
    link_video,
    ["http://remote.example/objects/123", link_html],
    [link_html, "http://remote.example/objects/123"],
    [link_html, link_video],
    [link_video, link_html],
    [link_video, {**link_html, "rel": "canonical"}],
    {"href": "https://notype.example/"},
]

examples_with_comment = [
    {
        "content": "See https://codeberg.org/funfedidev/fediverse-pasture-inputs/issues/66",
        "url": "http://pasture-one-actor/objects/123",
    }
]


data = InputData(
    title="Url Parameter",
    frontmatter="""Here we analyze varying url parameters.

The usage examples are inspired by Peertube's usage, see
[their documentation](https://docs.joinpeertube.org/api/activitypub#video).
""",
    filename="url.md",
    examples=[{"content": "text", "url": url} for url in url_examples]
    + examples_with_comment,
    detail_table=True,
    detail_extractor={
        "activity": lambda x: format_as_json(x.get("object", {}).get("url")),
        "mastodon": lambda x: pre_format(x.get("url")),
        "firefish": lambda x: pre_format(escape_markdown(x.get("url"))),
    },
    detail_title={
        "mastodon": "| url | url | Example |",
        "firefish": "| url | url | Example |",
    },
    support_table=False,
)
