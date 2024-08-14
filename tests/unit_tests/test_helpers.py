import pytest

from mod_manager.download_helpers import ModDownloader, VersionList
from mod_manager.exceptions import PackageMissingError


@pytest.fixture
def downloader(full_api):
    return ModDownloader(full_api)


@pytest.fixture
def downloader_no_deprecated(full_api):
    return ModDownloader(full_api, try_deprecated=False)


@pytest.fixture
def downloader_no_latest(full_api):
    return ModDownloader(full_api, use_latest_date=False)


@pytest.fixture
def version_list(temp_json_file):
    return VersionList.from_file(temp_json_file)


def test_version_list(downloader, version_list):
    out = downloader.get_download_list_by_name(
        ["NuclearLibrary"], ignore_dependencies=["BiggerLobby", "NuclearLibrary"]
    )
    assert out == version_list, f"Expected fake and real version list to match, got={out}, expected={version_list}"


def test_raises_error(downloader_no_deprecated):
    with pytest.raises(PackageMissingError):
        downloader_no_deprecated.get_download_list_by_name(["BiggerLobby"])


def test_too_many_versions(downloader_no_latest):
    with pytest.raises(ValueError, match="Got multiple versions/names for .*"):
        downloader_no_latest._get_mod_by_name("LethalPosters")
