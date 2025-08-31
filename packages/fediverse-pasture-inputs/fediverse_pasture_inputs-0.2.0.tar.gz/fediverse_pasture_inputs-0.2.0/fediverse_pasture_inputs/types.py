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


def value_from_dict_for_app(dictionary: dict, app: str, default="❌"):
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

        return lambda x: func(x) if x else default

    else:
        profile = app_to_profile_map.get(app, "mastodon")
        return value_from_dict_for_app(dictionary, profile, default=default)
    raise NameError("Unknown app %s", app)


@dataclass
class InputData:
    """Dataclass describing an input for an object support table

    :param title: Title of the support table
    :param frontmatter: Frontmatter describing why the support table exists
    :param details_frontmatter: Further explanation on details and support table.
    :param examples: List of dictionaries being added to the object
    :param filename: Name of generated markdown file

    :param support_table: Show a support table, i.e. one table table for all applications
    :param support_title: title for the entry corresponding to the activity
    :param support_result: Maps each application to the string to be shown

    :param detail_table: Show a detail table, i.e. a table for each applications
    :param detail_title: Maps application to the title line
    :param detail_extractor: Maps application to the corresponding fields. The result will be `detail_extractor["activity"] + detail_extractor[application] + ["example link"]`
    """

    title: str
    frontmatter: str
    examples: List[Dict]
    filename: str

    details_frontmatter: str = ""

    support_table: bool = False
    support_title: str | None = None
    support_result: Dict[str, Callable[[Dict], str]] = field(default_factory=dict)

    detail_table: bool = False
    detail_extractor: Dict[str, Callable[[Dict], List[str]]] = field(
        default_factory=dict
    )
    detail_title: Dict[str, str] = field(default_factory=dict)

    @property
    def docs_path(self):
        return to_docs_path(self.filename)

    def support_for_app(self, entry: Entry, app: str):
        extractor = value_from_dict_for_app(self.support_result, app)
        return entry.apply_to(app, extractor)

    def detail_for_app(self, entry: Entry, app: str):
        extractor = value_from_dict_for_app(self.detail_extractor, app, default=["❌"])
        return entry.apply_to(app, extractor)

    def detail_title_for_app(self, app: str):
        return value_from_dict_for_app(self.detail_title, app)
