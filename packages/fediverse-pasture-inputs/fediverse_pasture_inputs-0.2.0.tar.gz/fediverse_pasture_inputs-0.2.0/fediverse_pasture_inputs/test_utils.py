# SPDX-FileCopyrightText: 2023 Helge
# SPDX-FileCopyrightText: 2024 Helge
#
# SPDX-License-Identifier: MIT

from .utils import escape_markdown, format_as_json, pre_format


def test_escape_markdown():
    assert escape_markdown("`code`") == "\\`code\\`"


def test_format_as_json():
    data = {"cow": "moo"}
    formatted = format_as_json(data)

    assert formatted == [
        """<pre style="line-height:1;">{</pre><pre style="line-height:1;">  "cow": "moo"</pre><pre style="line-height:1;">}</pre>"""
    ]


def test_pre_format_bool():
    assert pre_format(True) == ["true"]
    assert pre_format(False) == ["false"]
