# SPDX-FileCopyrightText: 2024-present Joshua Luckie <luckie.joshua.c@gmail.com>
#
# SPDX-License-Identifier: MIT

import click
from .download_helpers import ModDownloader, ThunderstoreAPI
import requests, zipfile, io
from pathlib import Path
from datetime import datetime

@click.group()
@click.option('-c', '--community', default="lethal-company", help="Community package to download")
@click.option('-q', '--quiet', is_flag=True, default=False, help="Suppress output of finding packages")
@click.option('-p', '--package', multiple=True, default=[], help="Manually request packages by name")
@click.option('-f', '--file', type=click.Path(exists=True), help="File containing mods to search for, separated by new lines or commas", default=None)
@click.option('-o', '--output-directory', type=click.Path(exists=True, path_type=Path), help="Directory to write the zip files to", default=Path('.'))
@click.pass_context
def _main(ctx, quiet, community, file, package, output_directory):
    ctx.ensure_object(dict)
    ctx.obj['QUIET'] = quiet
    ctx.obj['COMMUNITY'] = community
    if file is not None:
        package.extend(file.readlines())
    ctx.obj['MODS'] = package
    ctx.obj['OUTPUT_DIRECTORY'] = output_directory

@_main.command()
@click.pass_context
def download(ctx):
    api = ThunderstoreAPI(ctx.obj['COMMUNITY'], quiet=ctx.obj['QUIET'])
    downloader = ModDownloader(api)
    version_list = downloader.get_download_list_by_name(ctx.obj['MODS'])
    output_dir = Path(ctx.obj['OUTPUT_DIRECTORY'], f"lethal-company-mods_{datetime.now().strftime('%Y_%m_%d')}")
    output_dir.mkdir(exist_ok=True, parents=True)
    downloader.download(version_list, output_dir)
    downloader.save_version_json(version_list)

def main(*args, **kwargs):
    return _main(*args, **kwargs, standalone_mode=False)
