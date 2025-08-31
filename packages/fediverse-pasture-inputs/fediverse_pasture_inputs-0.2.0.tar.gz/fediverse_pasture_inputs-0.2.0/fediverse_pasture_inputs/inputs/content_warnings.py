# SPDX-FileCopyrightText: 2023 Helge
# SPDX-FileCopyrightText: 2024 Helge
#
# SPDX-License-Identifier: MIT

from fediverse_pasture_inputs.types import InputData
from fediverse_pasture_inputs.utils import pre_format

content_warning_examples = [
    {
        "content": "text",
        "sensitive": True,
    },
    {
        "content": "text",
        "summary": "summary",
    },
    {
        "content": "text",
        "summary": "summary",
        "sensitive": True,
    },
    {
        "content": "see image",
        "attachment": {
            "type": "Image",
            "sensitive": True,
            "url": "http://pasture-one-actor/images/w001.png",
        },
    },
    {
        "content": "see image",
        "sensitive": True,
        "attachment": {
            "type": "Image",
            "sensitive": True,
            "url": "http://pasture-one-actor/images/w002.png",
        },
    },
    {
        "content": "see image",
        "attachment": {
            "content": "content",
            "type": "Image",
            "sensitive": True,
            "url": "http://pasture-one-actor/images/w003.png",
        },
    },
    {
        "content": "see image",
        "attachment": {
            "type": "Image",
            "summary": "summary",
            "sensitive": True,
            "url": "http://pasture-one-actor/images/w004.png",
        },
    },
]

data = InputData(
    title="Content Warnings",
    frontmatter="""Content Warnings are set using sensitive, then summary seems
to be used as a spoiler text.

The last three examples are an attempt to add a content warning to an image.""",
    filename="content_warnings.md",
    examples=content_warning_examples,
    detail_table=True,
    detail_extractor={
        "activity": lambda x: pre_format(x.get("object", {}).get("sensitive"))
        + pre_format(x.get("object", {}).get("summary")),
        "mastodon": lambda x: pre_format(x.get("sensitive"))
        + pre_format(x.get("spoiler_text")),
        "firefish": lambda x: pre_format(x.get("cw")),
    },
    detail_title={
        "mastodon": "| sensitive | summary | sensitive | spoiler_text | Example |",
        "firefish": "| sensitive | summary | cw  | Example |",
    },
)
