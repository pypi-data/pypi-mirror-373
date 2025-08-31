# SPDX-FileCopyrightText: 2023 Helge
# SPDX-FileCopyrightText: 2024 Helge
#
# SPDX-License-Identifier: MIT

from fediverse_pasture_inputs.types import InputData
from fediverse_pasture_inputs.utils import format_as_json

examples = [
    {
        "content": "Image",
        "attachment": [
            {
                "type": "Image",
                "url": "http://pasture-one-actor/assets/cow.jpg",
                "mediaType": "image/jpeg",
                "name": "a cow",
            }
        ],
    },
    {
        "content": "Video",
        "attachment": [
            {
                "type": "Video",
                "url": "http://pasture-one-actor/assets/cow_eating.mp4",
                "mediaType": "video/mp4",
                "name": "a cow eating grass",
            }
        ],
    },
    {
        "content": "Audio",
        "attachment": [
            {
                "type": "Audio",
                "url": "http://pasture-one-actor/assets/cow_moo.mp3",
                "mediaType": "audio/mpeg",
                "name": "the moo sound of a cow",
            }
        ],
    },
    {
        "content": "Audio as Document",
        "attachment": [
            {
                "type": "Document",
                "url": "http://pasture-one-actor/assets/cow_moo.mp3",
                "mediaType": "audio/mpeg",
                "name": "the moo sound of a cow",
            }
        ],
    },
    {"content": "Link", "attachment": {"href": "https://funfedi.dev", "type": "Link"}},
    {
        "content": "Payment Link, see FEP-0ea0",
        "attachment": {
            "type": "Link",
            "name": "Donate",
            "href": "payto://iban/DE75512108001245126199",
            "rel": "payment",
        },
    },
    {
        "content": "Text document",
        "attachment": {
            "type": "Document",
            "name": "text document",
            "url": "http://pasture-one-actor/assets/sample.txt",
        },
    },
    {
        "content": "Text document, href instead of url",
        "attachment": {
            "type": "Document",
            "name": "text document",
            "href": "http://pasture-one-actor/assets/sample.txt",
        },
    },
    {
        "content": "attached note",
        "attachment": {
            "type": "Note",
            "attributedTo": "http://pasture-one-actor/actor",
            "name": "attached note",
            "content": "This is just a note",
            "published": "2024-03-06T07:23:56Z",
        },
    },
    {
        "content": "Recipe",
        "attachment": {
            "@context": "https://schema.org/docs/jsonldcontext.jsonld",
            "@type": "Recipe",
            "name": "Peanut Butter and Jelly Sandwich",
            "recipeIngredient": [
                "Bread",
                "Peanut Butter",
                "Raspberry Jam",
                "Coffee (optional)",
            ],
            "recipeCategory": "Breakfast",
            "recipeInstructions": [
                {
                    "@type": "HowToStep",
                    "text": "Take a slice of bread and put it on a plate",
                },
                {"@type": "HowToStep", "text": "Spread peanut butter on the bread"},
                {
                    "@type": "HowToStep",
                    "text": "Spread raspberry jam on top of the peanut butter",
                },
                {
                    "@type": "HowToStep",
                    "text": "Eat your PB&J Sandwich and drink your coffee if you have it",
                },
                {
                    "@type": "HowToStep",
                    "text": "Check if you are still hungry, if yes a repeat step 1",
                },
            ],
        },
    },
    {
        "content": "10 images",
        "attachment": [
            {
                "type": "Document",
                "url": f"http://pasture-one-actor/images/10{x}.png",
            }
            for x in range(1, 11)
        ],
    },
]


def mastodon_has_attachment(resp):
    if not resp:
        return "❌"
    attachments = resp.get("media_attachments", [])
    if len(attachments) > 0:
        return "✅"
    return "-"


def misskey_has_attachment(resp):
    if not resp:
        return "❌"
    attachments = resp.get("files", [])
    if len(attachments) > 0:
        return "✅"
    return "-"


data = InputData(
    title="Attachments",
    frontmatter="""

In the support table:

- "✅" means at least one attachment,
- "-" means parsed
- "❌" means failed to parse

For more on image attachments see [Image Description](image_description.md)
and [Image Attachments](image_attachments.md).
""",
    filename="attachments.md",
    examples=examples,
    detail_table=True,
    detail_extractor={
        "activity": lambda x: format_as_json(x.get("object", {}).get("attachment")),
        "mastodon": lambda x: format_as_json(x.get("media_attachments")),
        "firefish": lambda x: format_as_json(x.get("files")),
    },
    detail_title={
        "mastodon": "| attributedTo | media_attachments | Ex. |",
        "firefish": "| attributedTo | files | Ex. |",
    },
    support_table=True,
    support_title="attachment",
    support_result={
        "activity": lambda x: format_as_json(
            x.get("object", {}).get("attachment"), small=True
        )[0],
        "mastodon": mastodon_has_attachment,
        "firefish": misskey_has_attachment,
    },
)
