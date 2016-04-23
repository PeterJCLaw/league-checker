#!/usr/bin/env python

from __future__ import print_function

import argparse
from collections import defaultdict, Counter
import math
import sys

def mean(numbers):
    assert numbers

    return sum(numbers) * 1.0 / len(numbers)

def variance(numbers):
    assert numbers

    mean_value = mean(numbers)

    sqaure_deviations = [(n - mean_value)**2 for n in numbers]

    return mean(sqaure_deviations)

def standard_deviation(numbers):
    assert numbers

    return math.sqrt(variance(numbers))


COMMENT_CHAR = '#'
SEPARATOR = '|'

parser = argparse.ArgumentParser('Displays statistics about how often a team is in a given corner')
parser.add_argument('-i', '--ignore-ids', help='comma separated list of ids to ignore')
parser.add_argument('schedule_file', help='schedule to examine')

args = parser.parse_args()

lines = []
with open(args.schedule_file, 'r') as f:
    for l in f.readlines():
        text = l.split(COMMENT_CHAR, 1)[0].strip()
        if text:
            lines.append(text)

#print("\n".join(lines))

teams = defaultdict(Counter)

for line in lines:
    teams_this_match = line.split(SEPARATOR)
    assert len(teams_this_match) % 4 == 0

    for pos, team_id in enumerate(teams_this_match):
        corner = pos % 4
        teams[int(team_id)][corner] += 1

if args.ignore_ids:
    for team_id in args.ignore_ids.split(','):
        team_id = int(team_id.strip())
        del teams[team_id]

infos = []

for team_id, corner_counts in teams.items():
    std_dev = standard_deviation(corner_counts.values())
    infos.append( (std_dev, team_id, corner_counts) )

infos.sort(reverse=True)

print(" Team |  Std. Dev. | Corner Counts")

for std_dev, team_id, corner_counts in infos:
    print("  {0:>2}  ".format(team_id), end='|')
    print("{0:>2.3f}".format(std_dev).center(12), end='|')

    for corner in range(4):
        count = corner_counts.get(corner)
        if count:
            count = "{0:>2}".format(count)
        else:
            count = '  '
        print(" {0}".format(count), end='')
    print('')
