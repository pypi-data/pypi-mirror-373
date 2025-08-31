# SPDX-FileCopyrightText: 2023 Helge
# SPDX-FileCopyrightText: 2024 Helge
#
# SPDX-License-Identifier: MIT

from fediverse_pasture_inputs.types import InputData
from fediverse_pasture_inputs.utils import pre_format, escape_markdown


html_tags = [
    f"<${tag}>${tag}</${tag}>"
    for tag in [
        "body",
        "html",
        "head",
        "title",
        "meta",
        "script",
        "article",
        "header",
        "footer",
        "form",
        "input",
        "select",
        "button",
    ]
]

data = InputData(
    title="HTML tags - that generally should not be supported",
    frontmatter="""
""",
    filename="html_bad.md",
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
