# SPDX-FileCopyrightText: 2023 Helge
# SPDX-FileCopyrightText: 2024 Helge
#
# SPDX-License-Identifier: MIT

from fediverse_pasture_inputs.types import InputData
from .html_tags import html_tags, details

data = InputData(
    title="HTML tags for article",
    frontmatter="""
Here we analyze, which types
of HTML tags are allowed inside the content field of `Article` type
objects. One should expect that a `Note`, i.e.

> Represents a short written work typically less than a single paragraph in length. 

see [here](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-note),
should not contain headings `h1-h6` or embedded media, e.g. `img`.

Sanitizing fields is
desired behavior as seen in [Section B.10 of ActivityPub](https://www.w3.org/TR/activitypub/#security-sanitizing-content).
""",
    filename="html_tags_article.md",
    group="HTML Tags",
    examples=[{"type": "Article", "content": content} for content in html_tags],
    details=details,
)
