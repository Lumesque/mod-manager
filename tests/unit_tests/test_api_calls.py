import pytest

from mod_manager.exceptions import InvalidVersionError


def test_thunderstore_api(api):
    assert not api._cache_index_by_name, "cache should be empty"
    mods = api.get_packages_by_name("BepInExPack")
    assert mods, "Package should be found"
    assert mods[0].has_version("5.4.2100"), "Package should have version 5.4.2100"
    assert api._cache_index_by_name, "Cache should be full"
    assert mods != api.get_packages_by_name(
        "BepInExPack", return_deprecated=True
    ), "Package mods should differ when looking for deprecated"


def test_package_not_found(full_api):
    mods = full_api.get_packages_by_name("ThisPackageDoesNotExistasasdfasdfasdfasd")
    assert not mods, "Package should not be found"


def test_version_not_found(full_api):
    with pytest.raises(InvalidVersionError):
        full_api.get_package_by_fullname("BepInEx-BepInExPack", "0000")
