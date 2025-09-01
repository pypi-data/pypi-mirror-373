import asyncio
import click
import zipfile
import os
import glob

from pathlib import Path
from fediverse_pasture_inputs import available

from .tool.format import page_from_inputs, add_samples_to_zip
from .tool.navigation import navigation_string


async def run_for_path(path):
    Path(path).mkdir(parents=True, exist_ok=True)

    for file in glob.glob(f"{path}/*"):
        os.unlink(file)
    for inputs in available.values():
        with open(f"{path}/{inputs.filename}", "w") as fp:
            await page_from_inputs(fp, inputs)


def write_navigation(path):
    Path(path).mkdir(parents=True, exist_ok=True)
    with open(f"{path}/.pages", "w") as fp:
        fp.write("nav:\n")
        fp.writelines(navigation_string())


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
@click.option("--no_navigation", is_flag=True, default=False)
def docs(path, no_navigation):
    """Creates a documentation page for each input"""

    asyncio.run(run_for_path(path))
    if not no_navigation:
        write_navigation(path)


@main.command()
@click.option(
    "--path",
    default="docs/inputs",
    help="Path of the directory the documentation pages are to be deposited",
)
def navigation(path):
    """Writes the .pages file for the inputs used to generate the documentation.
    Usually runs automatically when generating the documentation."""
    write_navigation(path)


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
