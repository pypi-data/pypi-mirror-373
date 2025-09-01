from . import current_asset_archive


def test_asset_archive():
    with current_asset_archive("0.1.8") as archive:
        names = archive.namelist()

        assert "assets/base.jsonap" in names
