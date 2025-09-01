# SPDX-FileCopyrightText: 2023-2025 Helge
#
# SPDX-License-Identifier: MIT

from fediverse_pasture_inputs.types import InputData

from .html_tags import details

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
The HTML tags tested here should probably not be supported
in Fediverse objects.
""",
    filename="html_bad.md",
    group="HTML Tags",
    examples=[{"content": content} for content in html_tags],
    details=details,
)
