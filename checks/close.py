#!/usr/bin/env python3

from __future__ import annotations

import argparse
import itertools
import collections
from typing import TypeVar, DefaultDict
from pathlib import Path
from collections.abc import Iterable

import helpers

T = TypeVar('T')

WARN_MIN_GAP = 2


def pairwise(iterable: Iterable[T]) -> Iterable[tuple[T, T]]:
    # From the docs at https://docs.python.org/3/library/itertools.html#itertools.pairwise
    # pairwise('ABCDEFG') --> AB BC CD DE EF FG
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)


def _sort_key(value: tuple[str, int, list[int], collections.Counter[int]]) -> tuple[int, helpers.HumanSortTuple]:
    tla, min_break, _, counts = value
    return min_break, -counts[min_break], helpers.human_sort_key(tla)


def main(schedule_file: Path) -> None:
    lines = helpers.load_lines(schedule_file)

    matches: DefaultDict[str, list[int]] = collections.defaultdict(list)
    breaks: DefaultDict[str, list[int]] = collections.defaultdict(list)

    match_num = 1

    for line in lines:
        teams = line.split(helpers.SEPARATOR)
        for tla in teams:
            matches[tla].append(match_num)

        match_num += 1

    min_breaks = []

    for tla, team_matches in matches.items():
        for last_match, match in pairwise(team_matches):
            diff = match - last_match
            breaks[tla].append(diff)
            last_match = match
        tla_breaks = breaks[tla]
        min_breaks.append((
            tla,
            min(tla_breaks),
            tla_breaks,
            collections.Counter(tla_breaks),
        ))

    print('Team\tMin-gap\tCount\tGaps')

    count_n = 0
    for tla, min_break, tla_breaks, counts in sorted(min_breaks, key=_sort_key):
        if min_break == WARN_MIN_GAP:
            count_n += 1
        print(f"{tla}\t{min_break}\t{counts[min_break]}\t{tla_breaks}")

    print()
    print(f"{count_n} teams have a minimum gap of {WARN_MIN_GAP}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=(
        "Displays statistics about how close the matches for all teams are. "
        "A min-gap of 3 indicates that a team has a match, followed by two"
        "match intervals off, and then another match."
    ))
    parser.add_argument('schedule_file', type=Path, help="Schedule file to inspect")
    return parser.parse_args()


if __name__ == '__main__':
    main(**parse_args().__dict__)
