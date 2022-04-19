#!/usr/bin/env python3

import argparse
import collections
from typing import List, Counter, DefaultDict
from pathlib import Path

import helpers


def main(schedule_file: Path) -> None:
    lines = helpers.load_lines(schedule_file)

    matches: DefaultDict[str, List[int]] = collections.defaultdict(list)
    breaks: DefaultDict[str, List[int]] = collections.defaultdict(list)

    match_num = 1

    for line in lines:
        teams = line.split('|')
        for tla in teams:
            matches[tla].append(match_num)

        match_num += 1

    min_breaks = []

    for tla, team_matches in matches.items():
        last_match = -25
        min_break = 200
        for match in team_matches:
            diff = match - last_match
            breaks[tla].append(diff)
            if diff < min_break:
                min_break = diff
            last_match = match
        min_breaks.append((tla, min_break, breaks[tla]))

    print('Team\tMin-gap\tCount\tGaps')

    count_n = 0
    for tla, min_break, btla in sorted(min_breaks, key=lambda x: x[1]):
        c: Counter[int] = collections.Counter()
        for x in sorted(btla):
            c[x] += 1
        if min_break == 2:
            count_n += 1
        print(f"{tla}\t{min_break}\t{c[min_break]}\t{btla}")

    print()
    print(count_n)


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
