import io
import json
import os
import warnings
import zipfile
from collections import Counter
from dataclasses import dataclass
from functools import reduce
from typing import List, NamedTuple, Optional

import click
import requests

from ..exceptions import PackageMissingError
from ..t_api import ModVersion, ThunderstoreAPI


class VersionList(NamedTuple):
    "List for versions and dependencies we ignore for specific names"

    versions: List[ModVersion]
    ignored_dependencies: Optional[List[str]]

    @classmethod
    def from_file(cls, json_file):
        # This is the versions json that is created by ModDownloader
        with open(json_file) as f:
            data = json.load(f)
        ignored_dependencies = data.pop("ignored_dependencies")
        return cls(versions=[ModVersion(**data[x]) for x in data], ignored_dependencies=ignored_dependencies)

    def to_dict(self):
        # This is the versions json that ModDownloader uses
        out = {}
        for vers in self.versions:
            out[vers.full_name] = vers.to_dict()
        out["ignored_dependencies"] = self.ignored_dependencies
        return out


@dataclass
class ModDownloader:
    api: ThunderstoreAPI
    # These are in case you don't find options, or find too many
    try_deprecated: bool = True
    use_latest_date: bool = True

    def download(self, list_of_versions, output_directory):
        _verses = list_of_versions.versions
        with click.progressbar(
            _verses, item_show_func=lambda x: x.name if x is not None else "", label="Downloading mod"
        ) as _list:
            for version in _list:
                download_url = version.download_url
                r = requests.get(download_url, stream=True, timeout=10)
                if not r.ok:
                    raise ValueError(f"Could not download from {download_url}")
                z = zipfile.ZipFile(io.BytesIO(r.content))
                z.extractall(output_directory)

    def get_download_list_by_name(self, list_of_mods, ignore_dependencies=None):
        mod_names = [self._get_mod_by_name(mod_name) for mod_name in list_of_mods]
        mod_names = self.handle_dependencies(mod_names, ignore_dependencies)
        out = [
            self.api.get_package_by_fullname(f"{owner}-{name}", owner=owner, version=version)
            for owner, name, version in [x.split("-") for x in set(mod_names)]
        ]
        return VersionList(reduce(lambda x, y: x + y, out), ignore_dependencies)

    def save_version_json(self, version_list, output_dir):
        with open(os.path.join(output_dir, "versions.json"), "w") as f:
            json.dump(version_list.to_dict(), f, indent=4)

    def _get_mod_by_name(self, mod_name):
        # There is no support for spaces, so use this instead
        mod_name = mod_name.replace(" ", "_")
        api = self.api
        out = api.get_packages_by_name(mod_name)
        if len(out) < 1:
            if self.try_deprecated:
                out = api.get_packages_by_name(mod_name, return_deprecated=True)
                if len(out) < 1:
                    raise PackageMissingError(mod_name)
                msg = f"{mod_name} is deprecated, this may not work! Using latest version found"
                warnings.warn(msg, stacklevel=2)
                return sorted(out, key=lambda x: x.get_latest().date_created)[-1]
            raise PackageMissingError(mod_name)
        elif len(out) > 1:
            if self.use_latest_date:
                warnings.warn(f"{mod_name} had multiple collision names, using one with latest date", stacklevel=2)
                return sorted(out, key=lambda x: x.get_latest().date_created)[-1]
            else:
                raise ValueError(f"Got multiple versions/names for {mod_name}, try using full name instead")
        return out[0]

    def handle_dependencies(self, downloadable_mods, ignore_dependencies=None):
        """
        Dependency handler. Checks the length of all unique names vs all the full names
        of the mods with their respective versions. For example,

        ['BepInEx-2100', 'BepInEx-25400'] will essentially compare
        {'BepInEx'} vs {'BepInEx-2100', 'BepInEx-25400'}

        in order to see if there is a dependency mismatch

        See check_conflicting_versions for more
        """
        dependencies = []
        if ignore_dependencies is None:
            ignore_dependencies = []
        for mod in downloadable_mods:
            latest = mod.get_latest()
            if latest.name in ignore_dependencies:
                continue
            dependencies.extend(latest.dependencies)
        # self.check_conflicting_versions(dependencies)
        dependencies.extend([x["full_name"] + "-" + x.get_latest().version_number for x in downloadable_mods])
        self.check_conflicting_versions(dependencies)
        return dependencies

    def check_conflicting_versions(self, full_name_list: List[str], ignore: bool = False):
        # TODO: make a flag where you choose which version you want to do either in an
        # interactive mode, or just say you'd like the one that is not deprecated -> latest date
        full_names = set(full_name_list)
        conflicts = Counter(["-".join(x.split("-")[:-1]) for x in full_names])
        for key, count in conflicts.items():
            if count > 1:
                corresponding_versions = {x for x in full_names if key in x}
                if not ignore:
                    raise ValueError(f"Found conflicting versions for {key}, got={corresponding_versions}")
