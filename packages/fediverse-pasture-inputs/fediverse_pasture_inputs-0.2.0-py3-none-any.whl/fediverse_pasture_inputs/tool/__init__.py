import tempfile
import zipfile

from typing import Generator
from contextlib import contextmanager
from urllib.request import urlretrieve

from fediverse_pasture_inputs.version import __version__


def make_url(tag):
    """Returns the url of the asset zip file

    ```pycon
    >>> make_url("0.1.8")
    'https://codeberg.org/api/packages/funfedidev/generic/fediverse_pasture_assets/0.1.8/fediverse_pasture_assets.zip'

    ```
    """
    return f"https://codeberg.org/api/packages/funfedidev/generic/fediverse_pasture_assets/{tag}/fediverse_pasture_assets.zip"


@contextmanager
def current_asset_archive(
    tag: str = __version__,
) -> Generator[zipfile.ZipFile, None, None]:
    """
    Downloads the zipfile for `tag` and then
    provides it as a generator.

    ```pycon
    >>> with current_asset_archive("0.1.8") as assets:
    ...     assets.namelist()
        ['assets/', 'assets/note2.jsonap', ...]

    ```

    :returns: archive of the inputs
    """
    with tempfile.TemporaryDirectory() as tmpdirname:
        filename = f"{tmpdirname}/assets.zip"
        urlretrieve(make_url(tag), filename)
        with zipfile.ZipFile(filename) as fp:
            yield fp


def extract(tag: str = __version__):
    """Extracts the asset zipfile"""
    with current_asset_archive(tag) as archive:
        archive.extractall()
