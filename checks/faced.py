#!/usr/bin/env python3

import argparse
import collections
from typing import Counter, DefaultDict
from pathlib import Path

import helpers


def main(schedule_file: Path, verbose: bool) -> None:
    matches = []
    lines = helpers.load_lines(schedule_file)
    for line in lines:
        players = line.split('|')
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

    for tla, opponents in c.items():
        missed = all_teams - set(opponents.keys())
        del opponents[tla]
        all_repeats = {}
        lots_repeats: Counter[str] = collections.Counter()
        faced = opponents.keys()
        for opp in faced:
            times = opponents[opp]
            if times > 1:
                all_repeats[opp] = times
            if times > LOTS_REPEATS_LIMIT:
                lots_repeats[opp] = times

        if verbose:
            print(f"{tla} faces {len(faced)} opponents: {faced}")
            print(f"{tla} repeats {len(all_repeats)} opponents: {all_repeats}")
            print(f"{tla} repeats {len(lots_repeats)} opponents lots of times: {lots_repeats}")
            print(f"{tla} misses {len(missed)} opponents: {missed}")
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
    parser.add_argument('--verbose', action='store_true', default=False)
    return parser.parse_args()


if __name__ == '__main__':
    main(**parse_args().__dict__)
