from io import StringIO

from fediverse_pasture_inputs.types import InputData

from .format import page_from_inputs


async def test_page_from_inputs():
    fp = StringIO()
    inputs = InputData("title", "frontmatter", examples="", filename="")

    await page_from_inputs(fp, inputs)

    contents = fp.getvalue()

    assert contents.startswith("# title")
