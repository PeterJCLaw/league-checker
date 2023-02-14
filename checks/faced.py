#!/usr/bin/env python3

import argparse
import collections
import dataclasses
from typing import Set, Dict, Tuple, Union, Counter, Collection, DefaultDict
from pathlib import Path

import helpers

TLA = str

_DEFAULT_VERBOSE = False


@dataclasses.dataclass(frozen=True)
class TeamFacings:
    tla: TLA
    opponents: Counter[TLA]
    lots_repeats: Counter[TLA]
    missed: Set[TLA]

    @classmethod
    def build(
        cls,
        tla: TLA,
        opponents: Counter[TLA],
        all_teams: Set[TLA],
        *,
        lots_repeats_limit: int,
    ) -> 'TeamFacings':
        missed = all_teams - opponents.keys()

        del opponents[tla]
        lots_repeats = collections.Counter({
            opp: times
            for opp, times in opponents.items()
            if times > lots_repeats_limit
        })

        return cls(
            tla,
            opponents,
            lots_repeats=lots_repeats,
            missed=missed,
        )

    @property
    def faced(self) -> Collection[str]:
        return self.opponents.keys()

    @property
    def repeats(self) -> Dict[TLA, int]:
        return {x: y for x, y in self.opponents.items() if y > 1}

    def sort_key(self) -> Tuple[int, Tuple[Union[str, int], ...]]:
        return -len(self.lots_repeats), helpers.human_sort_key(self.tla)


def join(values: Collection[str]) -> str:
    return ','.join(sorted(values))


def main(schedule_file: Path, verbose: bool = _DEFAULT_VERBOSE) -> None:
    matches = []
    lines = helpers.load_lines(schedule_file)
    for line in lines:
        players = line.split(helpers.SEPARATOR)
        while len(players) > 4:
            matches.append(players[0:4])
            players = players[4:]
        matches.append(players[0:4])

    c: DefaultDict[str, Counter[str]] = collections.defaultdict(collections.Counter)

    for match in matches:
        for tla in match:
            for faces in match:
                c[tla][faces] += 1

    all_teams = set(c.keys())

    # total appearances / teams => max appearances per team
    # 4.0 is teams-per-match
    matches_per_team = int(round(len(matches) * 4.0 / len(all_teams)))

    # 4.0 means this is 1/4 of a team's matches
    LOTS_REPEATS_LIMIT = int(round(matches_per_team / 4.0))

    facings = [
        TeamFacings.build(
            tla,
            opponents,
            all_teams,
            lots_repeats_limit=LOTS_REPEATS_LIMIT,
        )
        for tla, opponents in c.items()
    ]

    for team_facing in sorted(facings, key=lambda x: x.sort_key()):
        tla = team_facing.tla
        faced = team_facing.faced
        all_repeats = team_facing.repeats
        lots_repeats = team_facing.lots_repeats
        missed = team_facing.missed

        if verbose:
            print(f"{tla} faces {len(faced)} opponents: {join(faced)}")
            print(f"{tla} repeats {len(all_repeats)} opponents: {all_repeats}")
            print(f"{tla} repeats {len(lots_repeats)} opponents lots of times: {lots_repeats}")
            print(f"{tla} misses {len(missed)} opponents: {join(missed)}")
            print()
        else:
            print(
                f"{tla: <4} faces {len(faced): >2}, "
                f"misses {len(missed): >2}, "
                f"repeats {len(lots_repeats): >2} more than {LOTS_REPEATS_LIMIT} times",
                end="",
            )
            if len(lots_repeats) > 1:
                worst, count = lots_repeats.most_common(1)[0]
                if count > 10:
                    print(f" (including {worst} {count} times)", end="")
            print()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser("Displays statistics about which others a team have faced")
    parser.add_argument('schedule_file', help="schedule to examine")
    parser.add_argument('--verbose', action='store_true', default=_DEFAULT_VERBOSE)
    return parser.parse_args()


if __name__ == '__main__':
    main(**parse_args().__dict__)
