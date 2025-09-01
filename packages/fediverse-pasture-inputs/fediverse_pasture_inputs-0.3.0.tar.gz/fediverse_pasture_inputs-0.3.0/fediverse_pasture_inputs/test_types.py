# SPDX-FileCopyrightText: 2023 Helge
# SPDX-FileCopyrightText: 2024 Helge
#
# SPDX-License-Identifier: MIT

from fediverse_pasture.runner.entry import Entry

from .types import InputData, Support


def test_support_for_app():
    support = Support(
        title="test",
        result={
            "mastodon": lambda x: "a" + x.get("a", ""),
            "mastodon 4.2": lambda x: "b" + x.get("a", ""),
        },
    )
    data = InputData(
        title="title",
        frontmatter="frontmatter",
        examples=[],
        filename="test.md",
        support=support,
        group="group",
    )
    entry = Entry({"mastodon 4.1": {"a": "41"}, "mastodon 4.2": {"a": "42"}})

    assert data.support_for_app(entry, "mastodon 4.2") == "b42"
    assert data.support_for_app(entry, "mastodon 4.1") == "a41"
