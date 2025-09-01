# SPDX-FileCopyrightText: 2025 Helge
#
# SPDX-License-Identifier: MIT

from fediverse_pasture_inputs.types import InputData, Details, Support
from fediverse_pasture_inputs.utils import format_as_json

quotes_examples = [
    {
        "content": f"{name} attribute",
        name: "http://pasture-one-actor/assets/note1.jsonap",
    }
    for name in ["quote", "quoteUri", "quoteUrl", "_misskey_quote"]
] + [
    {
        "content": "FEP-e232 tag",
        "tag": [
            {
                "type": "Link",
                "mediaType": 'application/ld+json; profile="https://www.w3.org/ns/activitystreams"',
                "rel": "https://misskey-hub.net/ns#_misskey_quote",
                "href": "http://pasture-one-actor/assets/note1.jsonap",
            }
        ],
    },
]

support = Support(
    title="",
    result={
        "activity": lambda x: x.get("object", {}).get("content"),
        "mastodon": lambda x: "✅" if x.get("quote") else "❌",
        "pleroma": lambda x: "✅" if x.get("pleroma", {}).get("quote") else "❌",
        "misskey": lambda x: "✅" if x.get("renote") else "❌",
    },
)

details = Details(
    extractor={
        "activity": lambda x: format_as_json(x.get("object", {}).get("content")),
        "mastodon": lambda x: format_as_json(x.get("quote")),
        "pleroma": lambda x: format_as_json(x.get("pleroma", {}).get("quote")),
        "misskey": lambda x: format_as_json(x.get("renote")),
    },
    title={
        "mastodon": "| content | quote | Example |",
        "pleroma": "| content | pleroma.quote | Example |",
        "misskey": "| content | renote | Example |",
    },
)

data = InputData(
    title="Quotes",
    frontmatter="""
The examples are generated as follows. For `name` attribute, the object contains

```json
{
    "name": "http://pasture-one-actor/assets/note1.jsonap”
}
```

where name is one of `quote`, `quoteUri`, `quoteUrl`, `_misskey_quote`. For `FEP-e232 tag`, the quote is formatted according to [FEP-e232: Object Links](https://codeberg.org/fediverse/fep/src/branch/main/fep/e232/fep-e232.md), i.e.

```json
{
    "tag": [
        {
            "type": "Link",
            "mediaType": "application/ld+json; profile=\"https://www.w3.org/ns/activitystreams\"",
            "rel": "https://misskey-hub.net/ns#_misskey_quote",
            "href": "http://pasture-one-actor/assets/note1.jsonap",
        }
    ],
}
```

The various forms of a quote post are documented [here](https://codeberg.org/fediverse/fep/src/branch/main/fep/044f/fep-044f.md#compatibility-with-other-quote-implementations).
We note that the attribute examples treat the content as JSON and not as JSON-LD, i.e. the `@context` property is not modified. See [inputs#71](https://codeberg.org/funfedidev/fediverse-pasture-inputs/issues/71) for more information.
""",
    filename="quotes.md",
    group="Object Content",
    examples=quotes_examples,
    details=details,
    support=support,
)
