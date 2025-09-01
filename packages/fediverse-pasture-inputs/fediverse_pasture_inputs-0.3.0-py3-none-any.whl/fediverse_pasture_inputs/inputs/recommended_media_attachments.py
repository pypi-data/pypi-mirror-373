# SPDX-FileCopyrightText: 2023 Helge
# SPDX-FileCopyrightText: 2024 Helge
#
# SPDX-License-Identifier: MIT

from fediverse_pasture_inputs.types import InputData, Details, Support
from fediverse_pasture_inputs.utils import format_as_json

examples = [
    {
        "@context": [
            "https://www.w3.org/ns/activitystreams",
            "https://www.w3.org/ns/credentials/v2",
            {"size": "https://joinpeertube.org/ns#size"},
        ],
        "content": "Recommended Image Format",
        "attachment": [
            {
                "type": "Image",
                "name": "A beautiful cow",
                "url": "http://pasture-one-actor/assets/cow.jpg",
                "width": 100,
                "height": 162,
                "mediaType": "image/jpeg",
                "digestMultibase": "zQmaeDPzhNL32WQZnnzB1H6QJWvvFNEHdViDB71yrxyXU1t",
                "size": 9045,
            }
        ],
    },
    {
        "@context": [
            "https://www.w3.org/ns/activitystreams",
            "https://www.w3.org/ns/credentials/v2",
            {"size": "https://joinpeertube.org/ns#size"},
        ],
        "content": "Recommended Video Attachment",
        "attachment": [
            {
                "type": "Video",
                "url": "http://pasture-one-actor/assets/cow_eating.mp4",
                "name": "A beautiful cow eating",
                "width": 256,
                "height": 144,
                "mediaType": "video/mp4",
                "digestMultibase": "zQmSzK5qEe5tpjwGMhmjx9RvVoPkWhEmCwxP2s7wPMpKMoK",
                "size": 54373,
                "duration": "PT3S",
            }
        ],
    },
    {
        "@context": [
            "https://www.w3.org/ns/activitystreams",
            "https://www.w3.org/ns/credentials/v2",
            {"size": "https://joinpeertube.org/ns#size"},
        ],
        "content": "Recommended Audio Format",
        "attachment": [
            {
                "type": "Audio",
                "url": "http://pasture-one-actor/assets/cow_moo.mp3",
                "name": "A cow mooing",
                "mediaType": "audio/mpeg",
                "digestMultibase": "zQmSXTyLCPqoiGoUUwKRMKgFdddaAUkvQNr29nhB6tahb9Z",
                "size": 67709,
                "duration": "PT2.1S",
            }
        ],
    },
    {
        "@context": [
            "https://www.w3.org/ns/activitystreams",
            "https://www.w3.org/ns/credentials/v2",
            {"size": "https://joinpeertube.org/ns#size"},
        ],
        "content": "Multiple formats for video",
        "attachment": [
            {
                "type": "Video",
                "name": "A beautiful cow eating",
                "url": [
                    {
                        "type": "Link",
                        "size": 54373,
                        "digest": "zQmSzK5qEe5tpjwGMhmjx9RvVoPkWhEmCwxP2s7wPMpKMoK",
                        "width": 256,
                        "height": 144,
                        "href": "http://pasture-one-actor/assets/cow_eating.mp4",
                        "mediaType": "video/mp4",
                    },
                    {
                        "type": "Link",
                        "size": 2271723,
                        "digest": "zQme2X4rgWuRdmAtGGMSEbdoeRQ2NAL2VptcdRGTYDZbSKG",
                        "width": 1920,
                        "height": 1080,
                        "href": "http://pasture-one-actor/assets/cow_eating_hd.mp4",
                        "mediaType": "video/mp4",
                    },
                ],
                "duration": "PT3S",
            }
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


details = Details(
    extractor={
        "activity": lambda x: format_as_json(x.get("object", {}).get("attachment")),
        "mastodon": lambda x: format_as_json(x.get("media_attachments")),
        "misskey": lambda x: format_as_json(x.get("files")),
    },
    title={
        "mastodon": "| attributedTo | media_attachments | Ex. |",
        "misskey": "| attributedTo | files | Ex. |",
    },
)

support = Support(
    title="attachment",
    result={
        "activity": lambda x: x.get("object", {}).get("content"),
        "mastodon": mastodon_has_attachment,
        "misskey": misskey_has_attachment,
    },
)

data = InputData(
    title="Recommended Media Attachment Format",
    frontmatter="""
The first three example are our recommendation on how
to format image, video, and audio media attachments. Further
properties are possible, and might make it into this
recommendation at one point. Examples:

- Focal point and blurhash, see [Mastodon](https://docs.joinmastodon.org/spec/activitypub/#focalPoint)
- fps (frames per second) for videos

The final example cannot be recommended yet as it is not
widely supported. However, it illustrates how one can provide
multiple versions of the media attachments. A high quality and
low quality video in this case. The low quality video is enough
for most use cases, and is 40 times smaller.

The recommended format is documented in [FEP-1311: Media Attachments](https://codeberg.org/fediverse/fep/src/branch/main/fep/1311/fep-1311.md).

""",
    filename="recommended_attachments.md",
    examples=examples,
    group="Recommended Objects",
    details=details,
    support=support,
)
