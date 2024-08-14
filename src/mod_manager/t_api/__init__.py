from collections import UserDict, defaultdict
from dataclasses import dataclass, field, fields
from datetime import datetime
from typing import Dict, List, TypeVar, Union

import requests

from ..exceptions import InvalidVersion, PackageMissing


def cache_if_hasnt(func):
    def method(cls, *args, **kwargs):
        if not cls._has_cached_name:
            cls._cache_pkg_by_name()
            cls._has_cached_name = True
        return func(cls, *args, **kwargs)

    return method


@dataclass
class ModVersion:
    name: str
    full_name: str
    description: str
    version_number: str
    dependencies: list
    download_url: str
    downloads: int
    date_created: str
    website_url: str
    is_active: bool
    uuid4: str
    file_size: int

    def __post_init__(self):
        self.date_created = datetime.fromisoformat(self.date_created)

    def to_dict(self):
        return {
            "name": self.name,
            "full_name": self.full_name,
            "description": self.description,
            "version_number": self.version_number,
            "dependencies": self.dependencies,
            "download_url": self.download_url,
            "downloads": self.downloads,
            "date_created": self.date_created.isoformat(),
            "website_url": self.website_url,
            "is_active": self.is_active,
            "uuid4": self.uuid4,
            "file_size": self.file_size,
        }


class Mod(UserDict):
    def get_latest(self):
        return self.data["versions"][0]

    @property
    def versions(self):
        return [x.version_number for x in self.data["versions"]]

    def get_version(self, version: str) -> Union["Mod", None]:
        _vers = [x for x in self.data["versions"] if x.version_number == version]
        if not _vers:
            return None
        else:
            return _vers

    def has_version(self, version: str):
        return True if version in self.versions else False


@dataclass
class ThunderstoreAPI:
    community: str
    verbose: bool = field(default=True)
    lazy_cache: bool = field(default=False)
    community_url: str = field(init=False)
    package_url: str = field(init=False, repr=False)
    package_index: List[Dict] = field(init=False, repr=False)
    _cache_index_by_name: dict = field(default_factory=lambda: defaultdict(list), repr=False, init=False)
    _cache_index_by_fullname: dict = field(default_factory=dict, repr=False, init=False)
    _has_cached_name: bool = field(repr=False, init=False)

    def __post_init__(self):
        self.community_url = f"https://thunderstore.io/c/{self.community}/"
        self.package_url = self.community_url + "api/v1/package/"
        self.package_index = self._load_package_index()
        if not self.lazy_cache:
            self._has_cached_name = True
            self._cache_pkg_by_name()
        else:
            self._has_cached_name = False

    def _load_package_index(self) -> List:
        self.log("Getting index url...")
        r = requests.get(self.package_url)
        if r.status_code != 200:
            self.log(f"Error::{r.status_code}")
            return []
        self.log("Success")
        # This will return a list of jsons
        return [Mod(_out) for _out in r.json()]

    def _parse_pkg_item(self, pkg_dict, copy=False) -> Dict[str, Union[str, List[ModVersion]]]:
        if copy:
            pkg_dict = pkg_dict.copy()
        version_attrs = [x.name for x in fields(ModVersion)]
        versions = []
        for _version in pkg_dict["versions"]:
            arguments = {key: value for key, value in _version.items() if key in version_attrs}
            versions.append(ModVersion(**arguments))
        pkg_dict["versions"] = versions
        return pkg_dict

    def _cache_pkg_by_name(self):
        # Names are not exclusive, use index instead for later grabbing
        for i, _obj in enumerate(self.package_index):
            pkg_name = _obj["name"]
            self._cache_index_by_name[pkg_name].append(i)

    @cache_if_hasnt
    def get_packages_by_name(self, name, return_deprecated=False):
        # We can get multiple package names, so cacheing becomes difficult
        pkgs = [self.package_index[i] for i in self._cache_index_by_name[name] if name in self._cache_index_by_name]
        return [
            self._parse_pkg_item(_maybe_deprecated, copy=True)
            for _maybe_deprecated in pkgs
            if (return_deprecated or not _maybe_deprecated["is_deprecated"])
        ]

    def get_package_by_fullname(self, fullname, version, owner=None):
        vers_name = fullname + version
        _items = self.get_packages_by_name(fullname.split("-")[1], return_deprecated=True)
        for item in _items:
            if matches(item, fullname, owner):
                vers = item.get_version(version)
                if vers is None:
                    raise InvalidVersion(
                        f"Could not find a version {version} for {fullname}, available_versions: {item.versions}"
                    )
                return vers
        raise PackageMissing(f"Could not find a package with fullname {fullname} and owner {owner}")

    def log(self, msg):
        if self.verbose:
            print(msg)


def matches(_dict, full_name, owner=None):
    matches = []
    if owner is None:
        matches.append(True)
    else:
        matches.append(_dict["owner"] == owner)
    matches.append(_dict["full_name"] == full_name)
    return all(matches)
