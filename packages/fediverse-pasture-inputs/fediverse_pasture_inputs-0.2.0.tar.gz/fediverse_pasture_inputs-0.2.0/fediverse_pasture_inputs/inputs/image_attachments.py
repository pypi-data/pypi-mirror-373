# SPDX-FileCopyrightText: 2023 Helge
# SPDX-FileCopyrightText: 2024 Helge
#
# SPDX-License-Identifier: MIT

from fediverse_pasture_inputs.types import InputData
from fediverse_pasture_inputs.utils import format_as_json, safe_first_element


image_inline = {
    "@context": [
        "https://www.w3.org/ns/activitystreams",
        "https://www.w3.org/ns/credentials/v2",
        {"size": "https://joinpeertube.org/ns#size"},
    ],
    "type": "Image",
    "name": "A beautiful cow",
    "url": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/4QCuRXhpZgAASUkqAAgAAAAHABIBAwABAAAAAQAAABoBBQABAAAAYgAAABsBBQABAAAAagAAACgBAwABAAAAAgAAADEBAgANAAAAcgAAADIBAgAUAAAAgAAAAGmHBAABAAAAlAAAAAAAAABIAAAAAQAAAEgAAAABAAAAR0lNUCAyLjEwLjM2AAAyMDI1OjAzOjA2IDE5OjI1OjMwAAEAAaADAAEAAAABAAAAAAAAAP/hDM9odHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvADw/eHBhY2tldCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IlhNUCBDb3JlIDQuNC4wLUV4aXYyIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wTU09Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9tbS8iIHhtbG5zOnN0RXZ0PSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvc1R5cGUvUmVzb3VyY2VFdmVudCMiIHhtbG5zOkdJTVA9Imh0dHA6Ly93d3cuZ2ltcC5vcmcveG1wLyIgeG1sbnM6ZGM9Imh0dHA6Ly9wdXJsLm9yZy9kYy9lbGVtZW50cy8xLjEvIiB4bWxuczp4bXA9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC8iIHhtcE1NOkRvY3VtZW50SUQ9ImdpbXA6ZG9jaWQ6Z2ltcDo0ZWY2N2JmZC04NTlhLTRiYzMtYThjZC05YzY0MjQzNTNkYzciIHhtcE1NOkluc3RhbmNlSUQ9InhtcC5paWQ6ZDdjNDhmYjEtNmY5OC00NGE5LTg0MmMtYTE3NWRmZDUxMzc5IiB4bXBNTTpPcmlnaW5hbERvY3VtZW50SUQ9InhtcC5kaWQ6MWY4ODBiMWEtYTk5Zi00YTU2LWFiY2ItZTIzMmIzNWFhZjY2IiBHSU1QOkFQST0iMi4wIiBHSU1QOlBsYXRmb3JtPSJMaW51eCIgR0lNUDpUaW1lU3RhbXA9IjE3NDEyODU1MzExMTM1MTkiIEdJTVA6VmVyc2lvbj0iMi4xMC4zNiIgZGM6Rm9ybWF0PSJpbWFnZS9qcGVnIiB4bXA6Q3JlYXRvclRvb2w9IkdJTVAgMi4xMCIgeG1wOk1ldGFkYXRhRGF0ZT0iMjAyNTowMzowNlQxOToyNTozMCswMTowMCIgeG1wOk1vZGlmeURhdGU9IjIwMjU6MDM6MDZUMTk6MjU6MzArMDE6MDAiPiA8eG1wTU06SGlzdG9yeT4gPHJkZjpTZXE+IDxyZGY6bGkgc3RFdnQ6YWN0aW9uPSJzYXZlZCIgc3RFdnQ6Y2hhbmdlZD0iLyIgc3RFdnQ6aW5zdGFuY2VJRD0ieG1wLmlpZDozMWNjY2FlMy0xYmJiLTRjMDMtODI4NC0xMDJmNGU1YTFjNzkiIHN0RXZ0OnNvZnR3YXJlQWdlbnQ9IkdpbXAgMi4xMCAoTGludXgpIiBzdEV2dDp3aGVuPSIyMDI1LTAzLTA2VDE5OjI1OjMxKzAxOjAwIi8+IDwvcmRmOlNlcT4gPC94bXBNTTpIaXN0b3J5PiA8L3JkZjpEZXNjcmlwdGlvbj4gPC9yZGY6UkRGPiA8L3g6eG1wbWV0YT4gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA8P3hwYWNrZXQgZW5kPSJ3Ij8+/+ICsElDQ19QUk9GSUxFAAEBAAACoGxjbXMEQAAAbW50clJHQiBYWVogB+kAAwAGABIAGAAwYWNzcEFQUEwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAPbWAAEAAAAA0y1sY21zAAAAAAAAAAAAAAAAAAAAAAAAAAAA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",
    "width": 50,
    "height": 41,
    "mediaType": "image/jpeg",
    "digestMultibase": "zQmQVuinGXVKTeqesXeNA1vfWVJxiCpekcFQ6ESHLq2DHXf",
    "size": 5873,
}

image_examples = [
    {
        "content": "Format png",
        "attachment": {
            "type": "Document",
            "url": "http://pasture-one-actor/images/001.png",
        },
    },
    {
        "content": "Format png",
        "attachment": {
            "type": "Document",
            "url": "http://pasture-one-actor/images/001b.png",
            "mediaType": "image/png",
        },
    },
    {
        "content": "Format jpg",
        "attachment": {
            "type": "Image",
            "url": "http://pasture-one-actor/images/002.jpg",
        },
    },
    {
        "content": "Format jpg",
        "attachment": {
            "type": "Image",
            "url": "http://pasture-one-actor/images/002b.jpg",
            "mediaType": "image/jpeg",
        },
    },
    {
        "content": "Format svg",
        "attachment": {
            "type": "Image",
            "url": "http://pasture-one-actor/assets/FediverseLogo.svg",
        },
    },
    {
        "content": "Format eps",
        "attachment": {
            "type": "Image",
            "url": "http://pasture-one-actor/images/003.eps",
        },
    },
    {
        "content": "Format gif",
        "attachment": {
            "type": "Image",
            "url": "http://pasture-one-actor/images/003b.gif",
        },
    },
    {
        "content": "Format tiff",
        "attachment": {
            "type": "Image",
            "url": "http://pasture-one-actor/images/003c.tiff",
        },
    },
    {
        "content": "Format webp",
        "attachment": {
            "type": "Image",
            "url": "http://pasture-one-actor/images/003d.webp",
        },
    },
    {
        "content": "url does not exit",
        "attachment": {
            "type": "Document",
            "url": "http://pasture-one-actor/assets/does_not_exist.png",
        },
    },
    {
        "content": "Wrong height / width",
        "attachment": {
            "type": "Document",
            "width": 13,
            "height": 17,
            "url": "http://pasture-one-actor/images/004.png",
        },
    },
    {
        "content": "No type",
        "attachment": {
            "url": "http://pasture-one-actor/images/005.png",
        },
    },
    {
        "content": "url is Link object",
        "attachment": {
            "type": "Image",
            "url": {
                "type": "Link",
                "href": "http://pasture-one-actor/images/006.png",
            },
        },
    },
    {
        "content": "url is Link object with media type",
        "attachment": {
            "type": "Image",
            "url": {
                "type": "Link",
                "href": "http://pasture-one-actor/images/006b.png",
                "mediaType": "image/png",
            },
        },
    },
    {
        "content": "url is Link object in an array",
        "attachment": {
            "type": "Image",
            "url": [
                {
                    "type": "Link",
                    "href": "http://pasture-one-actor/images/006c.png",
                }
            ],
        },
    },
    {
        "content": "url is array of two Link objects",
        "attachment": {
            "type": "Image",
            "url": [
                {
                    "type": "Link",
                    "href": "http://pasture-one-actor/images/007.png",
                    "mediaType": "image/png",
                },
                {
                    "type": "Link",
                    "href": "http://pasture-one-actor/images/008.jpg",
                    "mediaType": "image/jpeg",
                },
            ],
        },
    },
    {"content": "inline image", "attachment": [image_inline]},
]


def mastodon_support(x):
    if not x:
        return "❌"
    media = x.get("media_attachments")
    if not media or len(media) == 0:
        return "-"
    comment = media[0].get("type", "-")
    if comment is None:
        return "-"
    return comment


def firefish_support(x):
    if not x:
        return "❌"
    media = x.get("files")
    if not media or len(media) == 0:
        return "-"
    comment = media[0].get("type", "-")
    if comment is None:
        return "-"
    return comment


data = InputData(
    title="Image Attachments",
    frontmatter="""The Image type is defined in
[ActivityStreams Vocabulary](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-image).

In the following, we test how various configurations of it are rendered.

A ❌ in the support table means that the entire message has failed to parse. A "-" means that the message was parsed, but
no attachment was generated. The text, e.g. `image` or
`unknown` is the the media type the Fediverse application
determined for the attachment.

We furthermore wish to point out that having several links
in the `url` property is useful to both offer the attachment
in different formats and say dimensions, e.g. one high resolution
and one low resolution one.
""",
    filename="image_attachments.md",
    examples=image_examples,
    detail_table=True,
    detail_extractor={
        "activity": lambda x: format_as_json(x.get("object", {}.get("attachment"))),
        "mastodon": lambda x: format_as_json(
            safe_first_element(x.get("media_attachments"))
        ),
        "firefish": lambda x: format_as_json(x.get("files"))
        + format_as_json(x.get("fileIds")),
    },
    detail_title={
        "mastodon": "| attachment | media_attachments | Example |",
        "firefish": "| attachment | files | fileIds | Example |",
    },
    support_table=True,
    support_title="attachment",
    support_result={
        "activity": lambda x: format_as_json(x["object"]["attachment"], small=True)[0],
        "mastodon": mastodon_support,
        "firefish": firefish_support,
    },
)
