# SPDX-FileCopyrightText: 2025 Helge
#
# SPDX-License-Identifier: MIT

from fediverse_pasture_inputs.types import InputData
from fediverse_pasture_inputs.utils import pre_format, escape_markdown


html_tags = [
    "<a href='https://funfedi.dev'>funfedi</a>",
    "<a href='https://funfedi.dev' hreflang='en'>hreflang en</a>",
    "<a href='https://funfedi.dev' target='_self'>target _self</a>",
    "<a href='https://funfedi.dev' target='_blank'>target _blank</a>",
    "<a href='https://funfedi.dev' class='fun-red-link'>fun-red-link class</a>",
    "<a href='https://funfedi.dev' class='mention'>class mention</a>",
    "<a href='https://funfedi.dev' class='hashtag'>class hashtag</a>",
    "<a href='https://funfedi.dev/assets/samples.zip' download='samples.zip'>download</a>",
] + [
    f"<a href='https://funfedi.dev' rel='${rel}'>rel ${rel}</a>"
    for rel in [
        "tag",
        "nofollow",
        "opener",
        "noopener",
        "noreferrer",
        "custom",
        "me",
        "external",
        "canonical",
        "alternate",
    ]
]

data = InputData(
    title="The anchor HTML tag",
    frontmatter="""The anchor HTML tag is used to create hyperlinks. See [MDN <a>: The Anchor element](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/a) for its description.

The goal here is to test variations of the attributes.
""",
    filename="html_anchor.md",
    examples=[{"content": content} for content in html_tags],
    detail_table=True,
    detail_extractor={
        "activity": lambda x: pre_format(
            x.get("object", {}).get("content"), pre_wrap=True
        ),
        "mastodon": lambda x: pre_format(x.get("content"), pre_wrap=True),
        "misskey": lambda x: pre_format(escape_markdown(x.get("text")), pre_wrap=True),
    },
    detail_title={
        "mastodon": "| content | content | Example |",
        "misskey": "| content | text | Example |",
    },
    support_table=False,
)
