# mod-manager

[![PyPI - Version](https://img.shields.io/pypi/v/mod-manager.svg)](https://pypi.org/project/mod-manager)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mod-manager.svg)](https://pypi.org/project/mod-manager)

-----

## Table of Contents

- [Installation](#installation)
- [License](#license)
- [About](#about)
- [Full list of arguments](#full-list-of-arguments)

## Installation

```console
pip install mod-manager
```

## License

`mod-manager` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

## About

mod-manager is a command line utility meant to help in downloading, searching, and version controlling mods from [thunderstore.io](https://thunderstore.io)

mod-manager works by using click context in order to pass around flags and values to the underlying commands. For this reason, most of the options that are necessary will need to be given to the main `tmm` command

It has 3 main utilities that get installed as a python binary under `tmm`
1. `tmm download`
    * `tmm download` takes no arguments in and of itself, but uses all the flags of the main top command. Heres an example command for downloading 'BepInExPack'
    ```bash
    > tmm -p BepInExPack download
    ```
2. `tmm redownload`
    * `tmm redownload` takes one argument, the json file which was output by the `tmm download`. `tmm download` creates a 'versions.json' that has all the settings and values from when the package\_index was downloaded
    ```bash
    > tmm redownload /path/to/versions.json
    ```
3. `tmm search`
    * `tmm search` takes any amount of arguments for searching using the package\_index that thunderstore provides. To show the actual output from the commands, you can use the `--no-suppress` flag to see what the script would grab for that specific variable, and `--only-latest` to only see the latest if you do choose to not suppress the output
    * The output looks like this
    ![searchoutput](./_pngs/search_output.png)


## Full list of arguments

1. `tmm`
    1. `-c`, `--community`, the commumity to use, defaults to 'lethal-company'
    2. `-q`, `--quiet`, will suppress outputs when retrieving the package index
    3. `-p`, `--package`, will include this package name in the search to grab from the package index and download, can use this multiple times ie: `-p BepInEx -p BiggerLobby`
    4. `-i`, `--ignore-dependencies`, similar to `-p` but this will exclude dependencies for that mod when it is found. ie: `-i BiggerLobby`
    5. `-f`, `--file`, use a file separated by new lines instead of using -p to look up for packages. If you want to mimic the capability of `--ignore-dependencies`, you can append `;ignore-dependencies` to the end of the string and it will add it to the list
    ```text
    BepInEx
    BiggerLobby;ignore-dependencies; Will ignore dependencies for BiggerLobby
    ```
    6. `-s`, `--no-save`, does __NOT__ save the mod versions found to a `versions.json` file
    7. `-o`, `--output-directory`, the directory in which to create the output folder, defaults to current directory
2. `download`
    N/A
3. `redownload`
    1. `json_file`, the json file `versions.json` that was made from using the `download` command
4. `search`
    1. `-l`, `--only-latest`, only show the latest version when outputing with `--no-suppression`
    2. `--show-all`, show all variants of the found mod and continue without looking further into the mod
    3. `-n`, `--no-suppress`, Output the json package data found from the thunderstore api
    4. `packages`, the list of mod names to search for with the thunderstore api
