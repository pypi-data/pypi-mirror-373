# SPDX-FileCopyrightText: 2023 Helge
# SPDX-FileCopyrightText: 2024 Helge
#
# SPDX-License-Identifier: MIT

from fediverse_pasture_inputs.types import InputData
from fediverse_pasture_inputs.utils import pre_format, escape_markdown
from .html_tags import html_tags

data = InputData(
    title="HTML tags in summary",
    frontmatter="""
Here we analyze, which types
of HTML tags are allowed inside the summary field.

As the [content field](./html_tags.md), the [summary field(https://www.w3.org/TR/activitystreams-vocabulary/#dfn-summary)
is described as 

> A natural language summarization of the object encoded as HTML.

This is a somewhat petulant table as most Fediverse applications
treat the summary field as a plain text content warning.

Sanitizing fields is
desired behavior as seen in [Section B.10 of ActivityPub](https://www.w3.org/TR/activitypub/#security-sanitizing-content).
""",
    filename="html_tags_summary.md",
    examples=[{"summary": content, "content": "See summary"} for content in html_tags],
    detail_table=True,
    detail_extractor={
        "activity": lambda x: pre_format(
            x.get("object", {}).get("summary"), pre_wrap=True
        ),
        "mastodon": lambda x: pre_format(x.get("spoiler_text"), pre_wrap=True)
        + pre_format(x.get("content"), pre_wrap=True),
        "misskey": lambda x: pre_format(escape_markdown(x.get("cw")), pre_wrap=True),
    },
    detail_title={
        "mastodon": "| summary | content | spoiler_text | Example |",
        "misskey": "| summary | cw | Example |",
    },
    support_table=False,
)
