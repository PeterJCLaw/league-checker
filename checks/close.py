#!/usr/bin/env python3

from __future__ import annotations

import random
import argparse
import functools
import itertools
import collections
import dataclasses
from typing import TypeVar, Callable, Protocol, DefaultDict
from pathlib import Path
from collections.abc import Iterable, Iterator, Sequence

import tqdm
import helpers
from helpers import Team, Schedule

T = TypeVar('T')

WARN_MIN_GAP = 2
NO_PERMUTE = 'none'
NO_PERMUTE_ADJUSTER = 'none'


@dataclasses.dataclass(frozen=True)
class TeamBreaks:
    tla: Team
    breaks: Sequence[int]

    @functools.cached_property
    def min_break(self) -> int:
        if not self.breaks:
            # Cope with teams with only one appearance. These don't have a
            # "break" as such since we don't count the start or end of the
            # overall schedule (which is intentional).
            return float('inf')  # type: ignore[return-value]
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


def compute_breaks(schedule: Schedule) -> list[TeamBreaks]:
    matches: DefaultDict[Team, list[int]] = collections.defaultdict(list)

    for match_num, teams in enumerate(schedule, start=1):
        for tla in teams:
            matches[tla].append(match_num)

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
        if gap <= 1:
            return float('inf')
        counts[gap] += 1
        return counts[gap] / gap

    return sum(gap_cost(x) for x in team_breaks.breaks)


def _score_many(min_breaks: list[TeamBreaks]) -> float:
    return sum(_score(x) for x in min_breaks)


def _random_permute(schedule: Schedule) -> Iterator[Schedule]:
    while True:
        out = list(schedule)
        random.shuffle(out)
        yield out


def _ordered_permute(schedule: Schedule) -> Iterator[Schedule]:
    return itertools.permutations(schedule)


class PermuteAdjuster(Protocol):
    def pre_adjust(self, schedule: Schedule) -> Schedule:
        ...

    def post_adjust(self, schedule: Schedule) -> Schedule:
        ...


class NoopAdjuster:
    def pre_adjust(self, schedule: Schedule) -> Schedule:
        return schedule

    def post_adjust(self, schedule: Schedule) -> Schedule:
        return schedule


class ReversingAdjuster:
    def pre_adjust(self, schedule: Schedule) -> Schedule:
        return list(reversed(schedule))

    def post_adjust(self, schedule: Schedule) -> Schedule:
        return list(reversed(schedule))


class SubsetAdjuster:
    whole: Schedule
    # TODO: add a way for these to be specified externally (probably CLI arguments)
    start = 46
    end = 68

    def pre_adjust(self, schedule: Schedule) -> Schedule:
        self.whole = schedule[:]
        return schedule[self.start: self.end]

    def post_adjust(self, schedule: Schedule) -> Schedule:
        return (  # type: ignore[no-any-return]
            self.whole[:self.start]  # type: ignore[operator]
            + list(schedule)
            + self.whole[self.end:]
        )


def _get_adjuster(permute_adjuster: str) -> PermuteAdjuster:
    registry: dict[str, type[PermuteAdjuster]] = {
        'subset': SubsetAdjuster,
        'reverse': ReversingAdjuster,
        NO_PERMUTE_ADJUSTER: NoopAdjuster,
    }
    return registry[permute_adjuster]()


def _handle_permutations(
    min_breaks: list[TeamBreaks],
    schedule: Schedule,
    permuter: Callable[[Schedule], Iterator[Schedule]],
    adjuster: PermuteAdjuster,
) -> Schedule:
    best: tuple[float, list[TeamBreaks], Schedule]
    best = (_score_many(min_breaks), min_breaks, schedule[:])

    print(best[0])

    try:
        schedule = adjuster.pre_adjust(schedule)

        bar = tqdm.tqdm(permuter(schedule))
        for permutation in bar:
            permutation = adjuster.post_adjust(permutation)
            min_breaks = compute_breaks(permutation)
            score = _score_many(min_breaks)
            if score < best[0]:
                bar.write(f"Better! {score}")
                best = (score, min_breaks, permutation)
    except KeyboardInterrupt:
        pass

    score, min_breaks, permutation = best
    print(score)

    return permutation


def main(
    schedule_file: Path,
    permute: str = NO_PERMUTE,
    permute_adjuster: str = NO_PERMUTE_ADJUSTER,
) -> None:
    schedule = helpers.load_schedule(schedule_file)

    min_breaks = compute_breaks(schedule)

    if permute != NO_PERMUTE:
        permutation = _handle_permutations(
            min_breaks,
            tuple(schedule),
            permuter={
                'random': _random_permute,
                'ordered': _ordered_permute,
            }[permute],
            adjuster=_get_adjuster(permute_adjuster),
        )

        if permutation == schedule:
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

        print('\n'.join(helpers.SEPARATOR.join(x) for x in permutation))


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
    parser.add_argument(
        '--permute-adjuster',
        choices=('reverse', 'subset', NO_PERMUTE_ADJUSTER),
        default=NO_PERMUTE_ADJUSTER,
        help="Adjust the lines before attempting to permute them",
    )
    return parser.parse_args()


if __name__ == '__main__':
    main(**parse_args().__dict__)
