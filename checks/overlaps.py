#!/usr/bin/env python

import argparse

import helpers

parser = argparse.ArgumentParser(
    "Highlights matches whose players overlap substantially with other matches",
)
parser.add_argument('schedule_file', help='schedule to examine')

args = parser.parse_args()

matches = []
lines = helpers.load_lines(args.schedule_file)

for line in lines:
    players = line.split('|')
    assert len(players) == 4, "Only matches of size 4 are currently supported"
    matches.append(set(players))

match_enumeration = tuple(enumerate(matches))

for idx, match in match_enumeration:
    for other_idx, other_match in match_enumeration[idx + 1:]:
        overlap = match & other_match
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
