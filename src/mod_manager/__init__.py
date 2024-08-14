# SPDX-FileCopyrightText: 2024-present Joshua Luckie <luckie.joshua.c@gmail.com>
#
# SPDX-License-Identifier: MIT

from datetime import datetime
from pathlib import Path

import click

from .__about__ import __version__
from .download_helpers import ModDownloader, VersionList
from .t_api import ThunderstoreAPI


@click.group()
@click.version_option(__version__)
@click.option("-c", "--community", default="lethal-company", help="Community package to download")
@click.option("-q", "--quiet", is_flag=True, default=False, help="Suppress output of finding packages")
@click.option("-p", "--package", multiple=True, default=[], help="Manually request packages by name")
@click.option(
    "-i", "--ignore-dependencies", multiple=True, default=[], help="Manually ignore package dependencies by name"
)
@click.option(
    "-f",
    "--file",
    type=click.Path(exists=True),
    help="File containing mods to search for, separated by new lines or commas",
    default=None,
)
@click.option(
    "-s",
    "--no-save",
    is_flag=True,
    default=False,
    help="Don't save a 'versions.json' file for future use with 'redownload'",
)
@click.option(
    "-o",
    "--output-directory",
    type=click.Path(exists=True, path_type=Path, dir_okay=True),
    help="Directory to write the zip files to",
    default=Path("."),
)
@click.pass_context
def _main(ctx, quiet, community, file, package, output_directory, no_save, ignore_dependencies):
    """
    Mod manager for thunderstore. This defaults to lethal company. It will create an output folder
    with the name of the date it was created as well as the community.
    """
    ctx.ensure_object(dict)
    ctx.obj["QUIET"] = quiet
    ctx.obj["COMMUNITY"] = community
    package = list(package)
    ignore_dependencies = list(ignore_dependencies)
    if file is not None:
        with open(file) as file:
            for line in file.readlines():
                pkg, *extras = line.strip().split(";")
                for x in extras:
                    if x == "ignore-dependencies":
                        ignore_dependencies.append(pkg)
                package.append(pkg)
    ctx.obj["MODS"] = package
    ctx.obj["IGNORE_DEPENDENCIES"] = ignore_dependencies
    current_time = datetime.now().strftime("%Y_%m_%d")
    output_dir = Path(output_directory, f"lethal-company-mods_{current_time}")
    output_dir.mkdir(exist_ok=True, parents=True)
    ctx.obj["OUTPUT_DIRECTORY"] = output_dir
    ctx.obj["SAVE"] = not no_save


@_main.command()
@click.argument("mod_name", nargs=-1)
@click.option("-l", "--only-latest", is_flag=True, default=False, help="Only download the latest version")
@click.option(
    "-n",
    "--no-suppress",
    is_flag=True,
    default=False,
    help="Show the output of the found package in json format as oppossed to JUST the details of the package",
)
@click.option("--show-all", is_flag=True, default=False, help="Show all found variants of the package")
@click.pass_context
def search(ctx, mod_name, only_latest, no_suppress, show_all):
    "Search for mods in the thunderstore.io website"
    from pprint import pprint

    api = ThunderstoreAPI(ctx.obj["COMMUNITY"], verbose=False)
    for mod in mod_name:
        print('Searching for "' + mod + '"...', end="")
        out = api.get_packages_by_name(mod)
        if len(out) == 0:
            out = api.get_packages_by_name(mod, return_deprecated=True)
            if len(out) == 0:
                click.secho("| NOT FOUND", fg="red")
                continue
        if len(out) == 1:
            out = out[0]
        elif show_all:
            pprint(out)
            continue
        else:
            print(" Found multiple results, using latest version...", end="")
            out = sorted(out, key=lambda x: x.get_latest().date_created)[-1]
        deprecated = out["is_deprecated"]
        latest = out.get_latest()
        date_created = latest.date_created.strftime("%Y-%m-%d")
        if only_latest:
            out = out.get_latest()

        if deprecated:
            click.secho("| DEPRECATED", fg="red", nl=False)
        else:
            click.secho("| NOT DEPRECATED", fg="green", nl=False)
        click.secho(" | LATEST VERSION: " + latest.version_number + " | DATE CREATED: " + date_created, fg="blue")
        if no_suppress:
            pprint(out)
        else:
            continue


@_main.command()
@click.pass_context
def download(ctx):
    "Download mods from the thunderstore.io website and create a folder of their outputs"
    api = ThunderstoreAPI(ctx.obj["COMMUNITY"], verbose=not ctx.obj["QUIET"])
    downloader = ModDownloader(api)
    version_list = downloader.get_download_list_by_name(
        ctx.obj["MODS"], ignore_dependencies=ctx.obj["IGNORE_DEPENDENCIES"]
    )
    downloader.download(version_list, ctx.obj["OUTPUT_DIRECTORY"])
    if ctx.obj["SAVE"]:
        downloader.save_version_json(version_list, ctx.obj["OUTPUT_DIRECTORY"])


@_main.command()
@click.argument("json_file", type=click.Path(exists=True))
@click.pass_context
def redownload(ctx, json_file):
    "Redownload mods from the thunderstore.io website and create a folder of their outputs using a past versions.json configuration"
    version_list = VersionList.from_file(json_file)
    downloader = ModDownloader(None)
    downloader.download(version_list, ctx.obj["OUTPUT_DIRECTORY"])
    if ctx.obj["SAVE"]:
        downloader.save_version_json(version_list, ctx.obj["OUTPUT_DIRECTORY"])


def main(*args, **kwargs):
    return _main(*args, **kwargs, standalone_mode=False)
