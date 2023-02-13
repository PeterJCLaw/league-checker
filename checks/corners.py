#!/usr/bin/env python3

import math
import random
import argparse
from typing import Optional, Sequence
from pathlib import Path
from itertools import chain
from collections import Counter, defaultdict

import helpers

_DEFAULT_NUM_CORNERS = 4


def mean(numbers):
    assert numbers

    return sum(numbers) * 1.0 / len(numbers)


def variance(numbers):
    assert numbers

    mean_value = mean(numbers)

    square_deviations = [(n - mean_value)**2 for n in numbers]

    return mean(square_deviations)


def standard_deviation(numbers):
    assert numbers

    return math.sqrt(variance(numbers))


def chunk(lst, size):
    assert len(lst) % size == 0
    chunks = []
    for lower in range(0, len(lst), size):
        chunk = lst[lower:lower + size]
        chunks.append(chunk)

    return chunks


def load_schedule(file_path, num_corners):
    schedule = []
    for line in helpers.load_lines(file_path):
        teams = line.split(helpers.SEPARATOR)
        assert len(teams) % num_corners == 0

        matches = chunk(teams, num_corners)
        schedule.append(matches)

    return schedule


def convert(schedule, teams_to_ignore=()):
    # Maps team -> corner -> count
    teams = defaultdict(Counter)

    for matches in schedule:
        for teams_this_match in matches:
            for corner, team_id in enumerate(teams_this_match):
                teams[team_id][corner] += 1

    for team_id in teams_to_ignore:
        del teams[team_id]

    return teams


def analyse(teams, num_corners):
    infos = []
    for team_id, corner_counts in teams.items():
        counts = list(corner_counts.values())
        counts += [0] * (num_corners - len(counts))
        std_dev = standard_deviation(counts)
        infos.append((std_dev, team_id, corner_counts))

    infos.sort(reverse=True)
    return infos


def print_info(infos):
    print(" Team |  Std. Dev. | Corner Counts")

    for std_dev, team_id, corner_counts in infos:
        print(f"  {team_id:>2}  ", end='|')
        print(f"{std_dev:>2.3f}".center(12), end='|')

        for corner in range(4):
            count = corner_counts.get(corner)
            if count:
                count = f"{count:>2}"
            else:
                count = '  '
            print(f" {count}", end='')
        print('')


def shuffle_all(schedule):
    for matches in schedule:
        for teams in matches:
            random.shuffle(teams)


def print_schedule(writer, schedule):
    for matches in schedule:
        teams = map(str, chain.from_iterable(matches))
        print(helpers.SEPARATOR.join(teams), file=writer)


def main(
    schedule_file: Path,
    num_corners: int = _DEFAULT_NUM_CORNERS,
    ignore_ids: Sequence[int] = (),
    fix: Optional[Path] = None,
) -> None:
    schedule = load_schedule(schedule_file, num_corners)
    assert schedule, "Schedule file was empty!"

    teams = convert(schedule, ignore_ids)

    infos = analyse(teams, num_corners)
    print_info(infos)

    if not fix:
        return

    shuffle_all(schedule)

    with open(fix, 'w') as f:
        print_schedule(f, schedule)


def ignore_ids_type(value: str) -> Sequence[int]:
    return [int(x) for x in value.split(',')]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        "Displays statistics about how often a team is in a given corner and "
        "optionally produces a schedule with randomized corners",
    )
    parser.add_argument(
        '-i',
        '--ignore-ids',
        type=ignore_ids_type,
        default=(),
        help="Comma separated list of ids to ignore.",
    )
    parser.add_argument(
        '--num-corners',
        type=int,
        help="The number of zones in the arena (default: %(default)s).",
        default=_DEFAULT_NUM_CORNERS,
    )
    parser.add_argument(
        '--fix',
        metavar='destination',
        type=Path,
        help=(
            "Randomize corner assignment within each match and output a new schedule "
            "to the given file."
        ),
    )
    parser.add_argument('schedule_file', type=Path, help="schedule to examine")

    return parser.parse_args()


if __name__ == '__main__':
    main(**parse_args().__dict__)
