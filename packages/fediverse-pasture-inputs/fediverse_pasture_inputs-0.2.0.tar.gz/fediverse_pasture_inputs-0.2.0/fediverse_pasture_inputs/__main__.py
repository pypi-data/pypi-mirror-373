import asyncio
import click
import zipfile
import os
import glob
import shutil

from pathlib import Path
from fediverse_pasture_inputs import available

from .tool.format import page_from_inputs, add_samples_to_zip


async def run_for_path(path):
    for file in glob.glob(f"{path}/*"):
        os.unlink(file)
    shutil.copyfile("./input_pages", f"{path}/.pages")
    for inputs in available.values():
        with open(f"{path}/{inputs.filename}", "w") as fp:
            await page_from_inputs(fp, inputs)


@click.group()
def main():
    """Tool for helping with creating the documentation for the
    fediverse-pasture-inputs"""
    ...


@main.command()
@click.option(
    "--path",
    default="docs/inputs",
    help="Path of the directory the documentation pages are to be deposited",
)
def docs(path):
    """Creates a documentation page for each input"""
    Path(path).mkdir(parents=True, exist_ok=True)
    asyncio.run(run_for_path(path))


@main.command()
@click.option(
    "--path",
    default="docs/assets",
    help="Path of the directory the zip file is created at",
)
def zip_file(path):
    """Creates a zip file containing the the generated ActivityPub objects
    and activities"""
    Path(path).mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(f"{path}/samples.zip", "w") as zipcontainer:
        for inputs in available.values():
            asyncio.run(add_samples_to_zip(zipcontainer, inputs))


if __name__ == "__main__":
    main()
