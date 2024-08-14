from dataclasses import dataclass, field, fields

from enum import Enum, auto
from typing import Any, List, Dict, ClassVar
from ..exceptions import PackageMissing
from functools import lru_cache
import requests
import inspect
import warnings
from datetime import datetime

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

@dataclass
class ListWrapper:

    package_index: List[Dict] = field(repr=False)
    cache: bool = field(default=True)
    quiet: bool = field(default=False)
    cache_obj: Dict = field(default_factory=dict, init=False)
    _loaded: bool = field(default = False, init=False, repr=False)

    def has_found_pkg(self, pkg):
        return pkg in self.cache_obj.keys()

    def has_pkg(self, pkg):
        if not self.has_found_pkg(pkg):
            out = self.search(pkg)
            if out is None:
                return False
            else:
                return True
        else:
            return True

    # Auto convert all packages into the cache
    def load(self):
        if self._loaded:
            warnings.warn("Package index has already been loaded and is being overwritten!")
        version_attrs = [x.name for x in fields(ModVersion)]
        for _obj in self.package_index:
            name = _obj['name']
            self.cache_obj[name] = self.parse_pkg_dict(_obj, copy=True)
        self._loaded = True
        return self

    def search(self, pkg):
        if self.has_found_pkg(pkg):
            return self.cache_obj[pkg]
        for _obj in self.package_index:
            name = _obj['name']
            self.cache_obj[name] = _obj
            # Dependencies are listed by full name
            if _obj['name'] == pkg:
                return _obj
        return None

    def parse_pkg_dict(self, pkg_dict, copy=False):
        if copy:
            pkg_dict = pkg_dict.copy()
        version_attrs = [x.name for x in fields(ModVersion)]
        versions = []
        for _version in pkg_dict['versions']:
            arguments = {key: value for key, value in _version.items() if key in version_attrs}
            versions.append(ModVersion(**arguments))
        pkg_dict['versions'] = versions
        return pkg_dict

    def get_pkg(self, pkg):
        if not self.has_pkg(pkg):
            raise PackageMissing(pkg)
        else:
            return self.cache_obj[pkg]

    @classmethod
    def from_url(cls, url, quiet=False, cache=True):
        index = requests.get(url)
        return cls(index.json(), quiet=quiet, cache=cache)

def download_mods(mod_list, url):
    pkg_index = ListWrapper.from_url(url).load()
    out = {}
    dependencies_to_look_for = []
    for mod in mod_list:
        # Getting latest
        mod_pkg = pkg_index.get_pkg(mod.replace(" ", "_"))['versions'][0]
        #mod_pkg = pkg_index.get_pkg(mod)['versions'][0]
        # The list will be empty if none so just use extend, skip the check
        dependencies_to_look_for.extend(mod_pkg.dependencies)
        out[mod] = mod_pkg
    for dependency in dependencies_to_look_for:
        category, pkg, version_number = dependency.split('-')
        if pkg in out:
            if out[pkg].version_number != version_number:
                raise ValueError(f"Version numbers do not match for pkg {pkg}, expected={version_number}, got={out[pkg].version_number}")
            else:
                mod_pkg = pkg_index.get_pkg(pkg)['versions'][0]
                out[pkg] = mod_pkg
    return out, dependencies_to_look_for
