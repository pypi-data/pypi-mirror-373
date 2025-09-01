# SPDX-FileCopyrightText: 2023 Helge
# SPDX-FileCopyrightText: 2024 Helge
#
# SPDX-License-Identifier: MIT

from fediverse_pasture_inputs.types import InputData, Details
from fediverse_pasture_inputs.utils import pre_format, format_as_json

details = Details(
    extractor={
        "activity": lambda x: pre_format(x.get("object", {}).get("content"))
        + format_as_json(x.get("object", {}).get("contentMap")),
        "mastodon": lambda x: pre_format(x.get("content", "-"))
        + pre_format(x.get("language", "-")),
        "firefish": lambda x: pre_format(x.get("text", "-")),
    },
    title={
        "mastodon": "| content | contentMap | content | language | Example |",
        "firefish": "| content | contentMap | text | Example |",
    },
)

data = InputData(
    title="Language support",
    frontmatter="""The content and contentMap properties are defined in the
[ActivityStreams Vocabulary](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-content).

The support for natural language values is described in
[ActivityStreams](https://www.w3.org/TR/activitystreams-core/#naturalLanguageValues).""",
    filename="language.md",
    group="Object Properties",
    examples=[
        {"content": "text"},
        {"content": "text", "contentMap": {"de": "Deutsch"}},
        {"content": "text", "contentMap": {"en": "English"}},
        {"content": "text", "contentMap": {"en": "English", "de": "Deutsch"}},
        {"content": "text", "contentMap": {"de": "Deutsch", "en": "English"}},
        {"contentMap": {"de": "Deutsch"}},
        {"contentMap": {"en": "English"}},
        {"contentMap": {"en": "English", "de": "Deutsch"}},
        {"contentMap": {"de": "Deutsch", "en": "English"}},
    ],
    details=details,
)
