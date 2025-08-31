# SPDX-FileCopyrightText: 2023 Helge
# SPDX-FileCopyrightText: 2024 Helge
#
# SPDX-License-Identifier: MIT

import html
import json

from typing import List


def is_supported(item):
    """
    Returns ✅ is item exists

    ```pycon
    >>> is_supported(None)
    ''

    >>> is_supported({"type": "Note"})
    '✅'

    ```
    """
    return "✅" if item else ""


def safe_first_element(item):
    """Returns the first element of a list, otherwise None

    ```pycon
    >>> safe_first_element([])

    >>> safe_first_element(None)

    >>> safe_first_element(["a", "b"])
    'a'

    ```
    """
    if not item or not isinstance(item, list) or len(item) == 0:
        return None
    return item[0]


def escape_markdown(text):
    """Escapes markdown characters, necessary to display markdown (as done for firefish)

    ```pycon
    >>> escape_markdown("*bold*")
    '\\\\*bold\\\\*'

    ```
    """

    if text is None:
        return "-"

    text = text.replace("`", "\\`")
    text = text.replace("*", "\\*")
    text = text.replace("_", "\\_")
    text = text.replace("[", "\\[")
    text = text.replace("]", "\\]")
    return text


def pre_wrapped(x, pre_wrap):
    """

    ```pycon
    >>> pre_wrapped("test", False)
    '<pre>test</pre>'

    >>> pre_wrapped("test", True)
    '<pre style="white-space: pre-wrap;">test</pre>'

    ```
    """
    style = ' style="white-space: pre-wrap;"' if pre_wrap else ""

    return f"<pre{style}>{html.escape(x)}</pre>"


def pre_format(text, pre_wrap=False):
    """Escapes html text to pre formatted markdown

    ```pycon
    >>> pre_format(True)
    ['true']

    >>> pre_format('<b>bold</b>\\n<i>italic</i>')
    ['<pre>&lt;b&gt;bold&lt;/b&gt;</pre><pre>&lt;i&gt;italic&lt;/i&gt;</pre>']

    ```
    """
    if text is None:
        return [""]
    if isinstance(text, bool):
        return ["true" if text else "false"]
    if isinstance(text, list):
        return sum((pre_format(x, pre_wrap=pre_wrap) for x in text), [])

    return ["".join(pre_wrapped(x, pre_wrap=pre_wrap) for x in text.split("\n"))]


def sanitize_backslash(x):
    return x.replace("|", "\\|")


def format_as_json(data: dict | None, small=False) -> List[str]:
    """Displays a dictionary as pretty printed json.

    ```pycon
    >>> format_as_json({"x": 1})
    ['<pre
        style="line-height:1;">{</pre><pre
        style="line-height:1;">  "x": 1</pre><pre
        style="line-height:1;">}</pre>']


    ```
    :param small: If true sets font-size to 75%."""

    style = "line-height:1;"
    if small:
        style += "font-size:75%;"

    return [
        "".join(
            f"""<pre style="{style}">{sanitize_backslash(x)}</pre>"""
            for x in json.dumps(data, indent=2).split("\n")
        )
    ]
