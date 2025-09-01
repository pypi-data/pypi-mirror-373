# SPDX-FileCopyrightText: 2023 Helge
# SPDX-FileCopyrightText: 2024 Helge
#
# SPDX-License-Identifier: MIT

import os
from dataclasses import dataclass, field
from typing import Dict, Callable, List

from fediverse_pasture.runner.entry import Entry


def to_docs_path(filename):
    return os.path.join("../../site/docs/support_tables/generated", filename)


app_to_profile_map = {
    "misskey": "firefish",
}
"""Maps app to profile used to generate details and support tables"""


def value_from_dict_for_app(
    dictionary: dict, app: str, default: str | list[str] = "❌"
):
    """Returns the value corresponding to app from dictionary
    by performing a lookup in [app_to_profile_map][fediverse_pasture_inputs.types.app_to_profile_map] and assuming `mastodon` is the default
    value.

    ```pycon
    >>> dictionary = {"known": "known",
    ...     "mastodon": "mastodon",
    ...     "firefish": "firefish"}
    >>> value_from_dict_for_app(dictionary, "unknown")
    'mastodon'

    >>> value_from_dict_for_app(dictionary, "known")
    'known'

    >>> value_from_dict_for_app(dictionary, "misskey")
    'firefish'

    ```
    """
    if app in dictionary:
        # FIXME Not sure if this is what I want ...
        func = dictionary.get(app)

        if isinstance(func, str):
            return func

        if func is None:
            raise ValueError(f"unknown function for app {app}")

        return lambda x: func(x) if x else default

    else:
        profile = app_to_profile_map.get(app, "mastodon")
        return value_from_dict_for_app(dictionary, profile, default=default)
    raise NameError("Unknown app %s", app)


@dataclass
class Support:
    """Configuration for the support table"""

    title: str = field(metadata={"description": "The title of the support"})
    result: dict[str, Callable[[dict], str]] = field(
        metadata={"description": "Mapping betweeen applications and the support result"}
    )


@dataclass
class Details:
    """Configuration for the details table"""

    title: dict[str, str] = field(metadata={"description": "The title line per app"})
    extractor: Dict[str, Callable[[Dict], List[str]]] = field(
        metadata={
            "description": "map of application / activity to the corresponding display in the details table"
        }
    )
    frontmatter: str | None = field(
        default=None,
        metadata={"description": "optional frontmatter to display before the details"},
    )


@dataclass
class InputData:
    """Dataclass describing an input for an object support table"""

    title: str = field(metadata={"description": "Title of the support table"})
    frontmatter: str = field(
        metadata={"description": "Frontmatter describing why the support table exists"}
    )
    examples: List[Dict] = field(
        metadata={"description": "List of dictionaries being added to the object"}
    )
    filename: str = field(metadata={"description": "Name of generated markdown file"})
    group: str = field(
        metadata={"description": "The group the example is to be displayed in"}
    )

    details: Details | None = field(
        default=None,
        metadata={"description": "How the details table will be generated"},
    )
    support: Support | None = field(
        default=None,
        metadata={"description": "If set, how the support table should be build"},
    )

    @property
    def docs_path(self):
        return to_docs_path(self.filename)

    def support_for_app(self, entry: Entry, app: str):
        if not self.support:
            raise ValueError("Support not available")
        extractor = value_from_dict_for_app(self.support.result, app)
        return entry.apply_to(app, extractor)

    def detail_for_app(self, entry: Entry, app: str):
        if not self.details:
            raise ValueError("Details not available")
        extractor = value_from_dict_for_app(self.details.extractor, app, default=["❌"])
        return entry.apply_to(app, extractor)  # type:ignore

    def detail_title_for_app(self, app: str):
        if not self.details:
            raise ValueError("Details not available")
        return value_from_dict_for_app(self.details.title, app)
