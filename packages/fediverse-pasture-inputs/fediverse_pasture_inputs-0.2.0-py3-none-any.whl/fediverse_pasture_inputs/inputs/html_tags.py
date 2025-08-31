# SPDX-FileCopyrightText: 2023 Helge
# SPDX-FileCopyrightText: 2024 Helge
#
# SPDX-License-Identifier: MIT

from fediverse_pasture_inputs.types import InputData
from fediverse_pasture_inputs.utils import pre_format, escape_markdown


html_tags = [
    "<b>bold</b>",
    "<strong>strong</strong>",
    "<i>italic</i>",
    """<i>italic with.</i> See <a href="https://codeberg.org/helge/funfedidev/issues/142">Issue 142</a>""",
    "<em>emphasis</em>",
    "<del>old</del><ins>new</ins>",
    "<s>stricken</s>",
    "<mark>mark</mark>",
    "find <var>x</var> (a variable)",
    "<ol><li>ordered</li></ol>",
    "<ul><li>unordered</li></ul>",
    "<h1>h1</h1>",
    "<h2>h2</h2>",
    "<h3>h3</h3>",
    "<h4>h4</h4>",
    "<h5>h5</h5>",
    "<h1>h1</h1><h2>h2</h2>",
    "<code>code</code>",
    "<pre>pre</pre>",
    "<blockquote>blockquote</blockquote>",
    "line<br/>break",
    "<p>paragraph</p>",
    "<small>small</small>",
    "<sup>sup</sup>",
    "<sub>sub</sub>",
    "<a href='https://funfedi.dev'>funfedi</a>",
    "<script>alert('hi');</script>",
    """<img src="http://pasture-one-actor/assets/nlnet.png" alt="NLNET Logo" />""",
    "wbr: Fernstraßen<wbr />bau<wbr />privat<wbr />finanzierungs<wbr />gesetz",
    """Audio <audio controls src="http://pasture-one-actor/assets/cow_moo.mp3"></audio>""",
    """Video <video controls width="250">
  <source src="http://pasture-one-actor/assets/cow_eating.mp4" type="video/mp4" />
  Video of a cow eating</video>""",
]

data = InputData(
    title="HTML tags",
    frontmatter="""Here we analyze, which types
of HTML tags are allowed inside the content field. Sanitizing fields is
desired behavior as seen in [Section B.10 of ActivityPub](https://www.w3.org/TR/activitypub/#security-sanitizing-content).

Due to firefish using markdown to format their content, the displayed result in the details table can be a bit off, please consult the example.
""",
    filename="html_tags.md",
    examples=[{"content": content} for content in html_tags],
    detail_table=True,
    detail_extractor={
        "activity": lambda x: pre_format(
            x.get("object", {}).get("content"), pre_wrap=True
        ),
        "mastodon": lambda x: pre_format(x.get("content"), pre_wrap=True),
        "misskey": lambda x: pre_format(escape_markdown(x.get("text")), pre_wrap=True),
    },
    detail_title={
        "mastodon": "| content | content | Example |",
        "misskey": "| content | text | Example |",
    },
    support_table=False,
)
