# SPDX-FileCopyrightText: 2023 Helge
# SPDX-FileCopyrightText: 2024 Helge
#
# SPDX-License-Identifier: MIT

from fediverse_pasture_inputs.types import InputData
from fediverse_pasture_inputs.utils import format_as_json

public_examples = [
    {
        "to": ["https://www.w3.org/ns/activitystreams#Public"],
        "content": "https://www.w3.org/ns/activitystreams#Public",
    },
    {"to": ["as:Public"], "content": "as:Public"},
    {"to": ["Public"], "content": "Public"},
]


data = InputData(
    title="Public addressing",
    frontmatter="""Public addressing is discussed [here](https://www.w3.org/TR/activitypub/#public-addressing). The essential point here is that
    `Public`, `as:Public`, and `https://www.w3.org/ns/activitystreams#Public`
    are equivalent as JSON-LD and thus should be treated in the same way
    by Fediverse applications.
""",
    filename="public_addressing.md",
    examples=public_examples,
    detail_table=False,
    support_table=True,
    support_title="to",
    support_result={
        "activity": lambda x: format_as_json(x["to"])[0],
        "mastodon": lambda x: "✅" if x else "❌",
        "firefish": lambda x: "✅" if x else "❌",
    },
)
