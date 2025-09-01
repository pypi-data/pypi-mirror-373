# SPDX-FileCopyrightText: 2023 Helge
# SPDX-FileCopyrightText: 2024 Helge
#
# SPDX-License-Identifier: MIT

from fediverse_pasture_inputs.types import InputData, Support, Details
from fediverse_pasture_inputs.utils import format_as_json, safe_first_element

image_description_examples = [
    {
        "content": "no description",
        "attachment": {
            "type": "Document",
            "url": "http://pasture-one-actor/images/100.png",
        },
    },
    {
        "content": "text",
        "attachment": {
            "type": "Document",
            "url": "http://pasture-one-actor/images/100.png",
            "name": "name",
            "summary": "summary",
            "content": "content",
        },
    },
    {
        "content": "text",
        "attachment": [
            {
                "type": "Document",
                "url": "http://pasture-one-actor/assets/FediverseLogo.png",
                "name": "name",
                "imageType": "image/jpeg",
            }
        ],
    },
    {
        "content": "no comment in attachment",
        "attachment": [
            {
                "type": "Document",
                "url": "http://pasture-one-actor/assets/FediverseLogo.png",
            }
        ],
    },
]


def mastodon_support(x):
    media = x.get("media_attachments")
    if not media or len(media) == 0:
        return "-"
    comment = media[0].get("description", "-")
    if comment is None:
        return "-"
    return comment


def misskey_support(x):
    media = x.get("files")
    if not media or len(media) == 0:
        return "-"
    comment = media[0].get("comment", "-")
    if comment is None:
        return "-"
    return comment


details = Details(
    extractor={
        "activity": lambda x: format_as_json(x.get("object", {}).get("attachment")),
        "mastodon": lambda x: format_as_json(
            safe_first_element(x.get("media_attachments"))
        ),
        "misskey": lambda x: format_as_json(x.get("files"))
        + format_as_json(x.get("fileIds")),
    },
    title={
        "mastodon": "| attachment | media_attachments | Example |",
        "misskey": "| attachment | files | fileIds | Example |",
    },
)

support = Support(
    title="attachment",
    result={
        "activity": lambda x: format_as_json(
            x.get("object", {}).get("attachment"), small=True
        )[0],
        "mastodon": mastodon_support,
        "misskey": misskey_support,
    },
)

data = InputData(
    title="Image Description",
    frontmatter="""The Image type is defined in
[ActivityStreams Vocabulary](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-image).

In this support table, we only consider how the image description, commonly called AltText is handled.
Image descriptions are important from an accessibility standpoint, see [WCAG 2.2. Text Alternatives](https://www.w3.org/TR/WCAG22/#text-alternatives).

It seems that certain implementations, e.g. misskey, store the image description on a per image URL basis and not for every instance of an image reference.
""",
    filename="image_description.md",
    group="Object Content",
    examples=image_description_examples,
    details=details,
    support=support,
)
