#!/usr/bin/env python3

from __future__ import annotations

import random
import argparse
import functools
import itertools
import collections
import dataclasses
from typing import TypeVar, DefaultDict
from pathlib import Path
from collections.abc import Iterable, Iterator, Sequence

import tqdm
import helpers

T = TypeVar('T')

WARN_MIN_GAP = 2
NO_PERMUTE = 'none'


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


def _sort_key(value: TeamBreaks) -> tuple[int, int, helpers.HumanSortTuple]:
    return value.min_break, -value.min_break_count, helpers.human_sort_key(value.tla)


def compute_breaks(lines: Sequence[str]) -> list[TeamBreaks]:
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


def _score(team_breaks: TeamBreaks) -> float:
    counts: collections.Counter[int] = collections.Counter()

    def gap_cost(gap: int) -> float:
        if gap == 1:
            return float('inf')
        counts[gap] += 1
        return counts[gap] / gap

    return sum(gap_cost(x) for x in team_breaks.breaks)


def _score_many(min_breaks: list[TeamBreaks]) -> float:
    return sum(_score(x) for x in min_breaks)


def _random_permute(lines: list[str]) -> Iterator[Sequence[str]]:
    while True:
        out = lines[:]
        random.shuffle(out)
        yield out


def _ordered_permute(lines: list[str]) -> Iterator[Sequence[str]]:
    return itertools.permutations(lines)


def main(schedule_file: Path, permute: str = NO_PERMUTE) -> None:
    lines = helpers.load_lines(schedule_file)
    original = lines[:]

    min_breaks = compute_breaks(lines)

    best: tuple[float, list[TeamBreaks], Sequence[str]]
    best = (_score_many(min_breaks), min_breaks, lines[:])

    if permute != NO_PERMUTE:
        print(best[0])

        permuter = {
            'random': _random_permute,
            'ordered': _ordered_permute,
        }[permute]

        try:
            bar = tqdm.tqdm(permuter(lines))
            for permutation in bar:
                min_breaks = compute_breaks(permutation)
                score = _score_many(min_breaks)
                if score < best[0]:
                    bar.write(f"Better! {score}")
                    best = (score, min_breaks, permutation)
        except KeyboardInterrupt:
            pass

        score, min_breaks, permutation = best
        print(score)

        if permutation == original:
            print("No improvement")
            return

    print('Team\tMin-gap\tCount\tGaps')

    count_n = 0
    for team_breaks in sorted(min_breaks, key=_sort_key):
        if team_breaks.min_break == WARN_MIN_GAP:
            count_n += 1
        print("\t".join(str(x) for x in (
            team_breaks.tla,
            team_breaks.min_break,
            team_breaks.min_break_count,
            team_breaks.breaks,
        )))

    print()
    print(f"{count_n} teams have a minimum gap of {WARN_MIN_GAP}")

    if permute != NO_PERMUTE:
        print()
        print()

        print("\n".join(permutation))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=(
        "Displays statistics about how close the matches for all teams are. "
        "A min-gap of 3 indicates that a team has a match, followed by two"
        "match intervals off, and then another match."
    ))
    parser.add_argument('schedule_file', type=Path, help="Schedule file to inspect")
    parser.add_argument(
        '--permute',
        choices=('random', 'ordered', NO_PERMUTE),
        default=NO_PERMUTE,
        help="Attempt to improve closeness by permuting the matches",
    )
    return parser.parse_args()


if __name__ == '__main__':
    main(**parse_args().__dict__)
