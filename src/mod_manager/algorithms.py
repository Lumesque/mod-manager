from dataclasses import dataclass
from typing import Iterable, List, NamedTuple, Optional


class FoundEntry(NamedTuple):
    match_positions: List[int]
    count: int
    fullstring: str
    percentmatch: float


@dataclass
class FuzzyFind:
    "Simple fuzzy search algorithm"

    iterable: Iterable[str]

    def __post_init__(self):
        if not all(isinstance(x, str) for x in self.iterable):
            raise TypeError(f"Expected iterable type to be a list of strings, got='{self.iterable}'")

    # This scan will search left to right until any match is found, and return the
    # highest non-zero match
    def search(self, value: str, limit: Optional[int] = None, case_insensitive=False) -> List[FoundEntry]:
        """
        Scan each iterable for the value

        Take for instance, ["AAA", "BBB", "CCC"], and the string "ADD",

        The results returned will be ["AAA"] since "AAA" has a non-zero match

        For the set ["AAA", "ABD", "CCC"], it will respectfully return
        ["ABD", "AAA"] since ABD has a higher match than AAA, but both have
        some form of a match

        If you want to exclude matches with a specific amount of the string,
        pass in the limit option

        For the set of ["AAA", "ABD", "ADD"] and the string "ADD", if the limit
        is 3, then only ["ADD"] will be returned, since it is the only string within
        the limit given

        For case insensitive matches, use 'case_insensitive=True'

        For teh set of ["Add", "AAA", "CCC"] and the string "add", with case_insensitive
        it will return ["Add", "AAA"]

        If no limit is given, it assumes the length of the string is the limit
        """
        if limit is None:
            limit = len(value)
        return self._search(value=value, limit=limit, case_insensitive=case_insensitive)

    def _search(self, value, limit, case_insensitive):
        # if case_insensitive:
        # iterable = (x.lower() for x in self.iterable)
        # value = value.lower()
        # else:
        # iterable = iter(self.iterable)
        founds = []
        for _str in iter(self.iterable):
            found = self.__count(value, _str, limit, case_insensitive=case_insensitive)
            if found:
                founds.extend(found)
        return founds

    def __count(self, value, string, limit, case_insensitive):
        counts = []
        size = len(value)
        if case_insensitive:
            search_str = string.lower()
            value = value.lower()
        else:
            search_str = string
        # Use i so we can refer to it in match_positions
        for i in range(size):
            pair = search_str[i : i + size]
            count = 0
            match_positions = []
            for num, (x, y) in enumerate(zip(value, pair)):
                if x == y:
                    count += 1
                    match_positions.append(num + i)
            if count >= limit:
                counts.append(FoundEntry(match_positions, count, fullstring=string, percentmatch=count / size))
        return counts
