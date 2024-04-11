#!/usr/bin/env python3

from __future__ import annotations

import argparse
import functools
import itertools
import collections
import dataclasses
from typing import TypeVar, DefaultDict
from pathlib import Path
from collections.abc import Iterable, Sequence

import helpers

WARN_MIN_GAP = 2

T = TypeVar('T')


@dataclasses.dataclass(frozen=True)
class TeamBreaks:
    tla: str
    breaks: Sequence[int]

    @functools.cached_property
    def min_break(self) -> int:
        return min(self.breaks)

    @functools.cached_property
    def counts(self) -> collections.Counter[int]:
        return collections.Counter(self.breaks)

    @functools.cached_property
    def min_break_count(self) -> int:
        return self.counts[self.min_break]


def pairwise(iterable: Iterable[T]) -> Iterable[tuple[T, T]]:
    # From the docs at https://docs.python.org/3/library/itertools.html#itertools.pairwise
    # pairwise('ABCDEFG') --> AB BC CD DE EF FG
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)


def _sort_key(value: TeamBreaks) -> tuple[int, helpers.HumanSortTuple]:
    return value.min_break, -value.min_break_count, helpers.human_sort_key(value.tla)


def compute_breaks(lines: list[str]) -> list[Breaks]:
    matches: DefaultDict[str, list[int]] = collections.defaultdict(list)

    match_num = 1

    for line in lines:
        teams = line.split(helpers.SEPARATOR)
        for tla in teams:
            matches[tla].append(match_num)

        match_num += 1

    min_breaks = []

    for tla, team_matches in matches.items():
        breaks = []
        for last_match, match in pairwise(team_matches):
            diff = match - last_match
            breaks.append(diff)
            last_match = match
        min_breaks.append(TeamBreaks(tla, breaks))

    return min_breaks


def main(schedule_file: Path) -> None:
    lines = helpers.load_lines(schedule_file)

    min_breaks = compute_breaks(lines)

    print('Team\tMin-gap\tCount\tGaps')

    count_n = 0
    for team_breaks in sorted(min_breaks, key=_sort_key):
        if team_breaks.min_break == WARN_MIN_GAP:
            count_n += 1
        print(f"{team_breaks.tla}\t{team_breaks.min_break}\t{team_breaks.min_break_count}\t{team_breaks.breaks}")

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
