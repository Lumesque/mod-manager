# mod-manager

[![PyPI - Version](https://img.shields.io/pypi/v/mod-manager.svg)](https://pypi.org/project/mod-manager)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mod-manager.svg)](https://pypi.org/project/mod-manager)

-----

## Table of Contents

- [Installation](#installation)
- [License](#license)
- [About](#about)
- [Fuzzy searching](#fuzzy-searching)
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
3. `tmm fsearch`
    * `tmm fsearch` searches through the index using a simple Fuzzy searching algorithm, and returns found deprecated and non-deprecated packages. To exclude deprecated packages, use `--no-deprecated` or `-n`. If you want to search case insensitive, use the `-i` or `--case-insensitive` flag
4. `tmm search` DEPRECATED
    * `tmm search` IS DEPRECATED, and will not be kept/upheld. For the current search, see [Fuzzy Searching](#fuzzy-searching)
    * `tmm search` takes any amount of arguments for searching using the package\_index that thunderstore provides. To show the actual output from the commands, you can use the `--no-suppress` flag to see what the script would grab for that specific variable, and `--only-latest` to only see the latest if you do choose to not suppress the output
    * The output looks like this
    ![searchoutput](./_pngs/search_output.png)

## Fuzzy searching
* Currently `tmm` uses a simple fuzzy searching algorithm. It works by moving the string from left to right along the search value and counting how many letters match

Take the below example
```python
string = "ABC"
```
In order to fuzzy search, the program instantiates a class with a list of strings
```python
from mod_manager.algorithms import FuzzyFind
searcher = FuzzyFind(["AAA", "BBB", "CCC", "ABD", "ABC"])
```
The fuzzy searcher will then return the found entries with the count of what positions matched as it moved along the string. At first, the search will return only full matches in the string
```python
> searcher.search(string) # searcher.search("ABC")
[FoundEntry(match_positions=[0,1,2], count=3, fullstring='ABC', percentage=1.0)]
```
To change this behavior, the limit option can be used in order to allow for different options (keep in mind, this can lead to duplicate search values as there can be multiple matches)

```python
> searcher.search(string, limit=1)
[
Foundentry(match_positions=[0], count=1, fullstring='AAA', percentmatch=0.33),
Foundentry(match_positions=[1], count=1, fullstring='AAA', percentmatch=0.33),
Foundentry(match_positions=[2], count=1, fullstring='AAA', percentmatch=0.33),
...
]
```

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
4. `fsearch`
    1. `-n`, `--no-deprecated`, Don't include deprecated packages in search
    2. `-l`, `--limit`, Match limit for fuzzy finder, defaults to length of string passed in
    3. `-i`, `--case-insensitive`, Search for packages without case sensitivity
5. `search` DEPRECATED
    1. `-l`, `--only-latest`, only show the latest version when outputing with `--no-suppression`
    2. `--show-all`, show all variants of the found mod and continue without looking further into the mod
    3. `-n`, `--no-suppress`, Output the json package data found from the thunderstore api
    4. `packages`, the list of mod names to search for with the thunderstore api
