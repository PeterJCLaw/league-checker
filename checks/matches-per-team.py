from __future__ import annotations

import argparse
import collections
from typing import Counter
from pathlib import Path

import helpers


def main(schedule_file: Path) -> None:
    lines = helpers.load_lines(schedule_file)

    counter: Counter[str] = collections.Counter()

    for match in lines:
        teams = match.split(helpers.SEPARATOR)
        for team in teams:
            counter[team] += 1

    for entrant, count in counter.most_common():
        print(f"{entrant}: {count}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=(
        "Prints the number of matches each team has, sorted by match count."
    ))
    parser.add_argument('schedule_file', type=Path, help="File to search and modify")
    return parser.parse_args()


if __name__ == '__main__':
    main(**parse_args().__dict__)
