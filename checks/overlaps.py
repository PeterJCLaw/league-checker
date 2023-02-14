#!/usr/bin/env python3

from __future__ import annotations

import argparse
import collections
from typing import DefaultDict
from pathlib import Path

import helpers


def main(schedule_file: Path) -> None:
    matches = []
    lines = helpers.load_lines(schedule_file)

    for line in lines:
        players = line.split(helpers.SEPARATOR)
        assert len(players) == 4, "Only matches of size 4 are currently supported"
        matches.append(set(players))

    match_enumeration = tuple(enumerate(matches))

    # Size of overlap -> match numbers
    overlaps: DefaultDict[int, list[tuple[int, int]]] = collections.defaultdict(list)

    for idx, match in match_enumeration:
        for other_idx, other_match in match_enumeration[idx + 1:]:
            overlap = match & other_match

            if len(overlap) <= 2:
                continue

            overlaps[len(overlap)].append((idx, other_idx))

            if len(overlap) == 4:
                print("Match {} is identical to match {}: both contain {}".format(
                    idx,
                    other_idx,
                    ','.join(sorted(match)),
                ))
            elif len(overlap) == 3:
                print("Match {} overlaps with match {}: {} vs {}".format(
                    idx,
                    other_idx,
                    ','.join(sorted(match)),
                    ','.join(sorted(other_match)),
                ))

    print()
    print("Overlap summary")
    for size, overlapping_matches in overlaps.items():
        print(f" Size {size}: {len(overlapping_matches)}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        "Highlights matches whose players overlap substantially with other matches",
    )
    parser.add_argument('schedule_file', help='schedule to examine')
    return parser.parse_args()


if __name__ == '__main__':
    main(**parse_args().__dict__)
