#!/usr/bin/env python3

import argparse
import collections
from pathlib import Path

import helpers


def main(schedule_file: Path) -> None:
    schedule = helpers.load_schedule(schedule_file)

    bad_matches = [
        (match_num, teams)
        for match_num, teams in enumerate(schedule)
        if len(set(teams)) != len(teams)
    ]

    if bad_matches:
        print("WARNING: Some matches contain two concurrent appearances for the same team:")
        print()
        for match_num, teams in bad_matches:
            affected = [x for x, y in collections.Counter(teams).items() if y > 1]
            print(f"{match_num}: {helpers.SEPARATOR.join(teams)}  # Affected: {', '.join(affected)}")
    else:
        print('Is valid')


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=(
        "Checks that teams only appear once per match (i.e: row) of the schedule."
    ))
    parser.add_argument('schedule_file', type=Path, help="File to check")
    return parser.parse_args()


if __name__ == '__main__':
    main(**parse_args().__dict__)
