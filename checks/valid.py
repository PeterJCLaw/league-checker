#!/usr/bin/env python3

import argparse
from pathlib import Path

import helpers


def main(schedule_file: Path, teams_file: Path) -> None:
    all_teams = [x.strip() for x in teams_file.read_text().splitlines(keepends=False)]

    lines = helpers.load_lines(schedule_file)

    found_teams = []

    for line in lines:
        teams = [x.strip() for x in line.split(helpers.SEPARATOR)]
        assert len(set(teams)) == len(teams) == 4, teams
        found_teams += teams

    # Sanity
    assert len(set(all_teams)) == len(all_teams), all_teams

    # Sanity
    missing_teams = set(all_teams) - set(found_teams)
    print(', '.join(missing_teams))
    assert len(set(found_teams)) == len(all_teams)

    print('Is valid')


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=(
        "Ensures that all the teams listed (one TLA per line) are in the schedule"
    ))
    parser.add_argument('schedule_file', type=Path, help="File to check")
    parser.add_argument(
        'teams_file',
        help="File containing a list of all entrants, one per line",
    )
    return parser.parse_args()


if __name__ == '__main__':
    main(**parse_args().__dict__)
