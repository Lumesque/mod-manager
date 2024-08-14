import io

import pytest

from mod_manager.t_api import ThunderstoreAPI


@pytest.fixture
def api():
    return ThunderstoreAPI("lethal-company", lazy_cache=True)


@pytest.fixture(scope="module")
def full_api():
    return ThunderstoreAPI("lethal-company", lazy_cache=False)


def fake_json_file():
    return io.StringIO("""
{
    "NiceHairs-NuclearLibrary-1.0.7": {
        "name": "NuclearLibrary",
        "full_name": "NiceHairs-NuclearLibrary-1.0.7",
        "description": "My Library for easy mod development.",
        "version_number": "1.0.7",
        "dependencies": [
            "BepInEx-BepInExPack-5.4.2100"
        ],
        "download_url": "https://thunderstore.io/package/download/NiceHairs/NuclearLibrary/1.0.7/",
        "downloads": 46324,
        "date_created": "2024-07-25T08:20:34.640527+00:00",
        "website_url": "",
        "is_active": true,
        "uuid4": "c0b506c3-8893-4fca-beec-562542935051",
        "file_size": 56913
    },
    "ignored_dependencies": [
        "BiggerLobby"
    ]
}
                        """)


@pytest.fixture
def temp_json_file(tmp_path):
    # tmp_path.write_text(fake_json_file())
    file = tmp_path / "versiosn_list.json"
    file.write_text(
        """
{
    "NiceHairs-NuclearLibrary-1.0.7": {
        "name": "NuclearLibrary",
        "full_name": "NiceHairs-NuclearLibrary-1.0.7",
        "description": "My Library for easy mod development.",
        "version_number": "1.0.7",
        "dependencies": [
            "BepInEx-BepInExPack-5.4.2100"
        ],
        "download_url": "https://thunderstore.io/package/download/NiceHairs/NuclearLibrary/1.0.7/",
        "downloads": 46324,
        "date_created": "2024-07-25T08:20:34.640527+00:00",
        "website_url": "",
        "is_active": true,
        "uuid4": "c0b506c3-8893-4fca-beec-562542935051",
        "file_size": 56913
    },
    "ignored_dependencies": [
        "BiggerLobby",
        "NuclearLibrary"
    ]
}
                        """
    )
    return file
