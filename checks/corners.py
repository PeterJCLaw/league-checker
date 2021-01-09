#!/usr/bin/env python

from __future__ import print_function

import argparse
from collections import defaultdict, Counter
from itertools import chain
import math
import random
import sys

import helpers

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


def chunk(lst, size=4):
    assert len(lst) % size == 0
    chunks = []
    for lower in range(0, len(lst), size):
        chunk = lst[lower:lower+size]
        chunks.append(chunk)

    return chunks


def load_schedule(file_path):
    schedule = []
    for line in helpers.load_lines(file_path):
        teams = line.split(helpers.SEPARATOR)
        assert len(teams) % 4 == 0

        matches = chunk(teams, 4)
        schedule.append(matches)

    return schedule

def convert(schedule, teams_to_ignore=()):
    # Maps team -> corner -> count
    teams = defaultdict(Counter)

    for match_id, matches in enumerate(schedule):
        for teams_this_match in matches:
            for corner, team_id in enumerate(teams_this_match):
                teams[team_id][corner] += 1

    for team_id in teams_to_ignore:
        del teams[team_id]

    return teams

def analyse(teams):
    infos = []
    for team_id, corner_counts in teams.items():
        counts = corner_counts.values()
        counts += [0] * (4 - len(counts))
        std_dev = standard_deviation(counts)
        infos.append( (std_dev, team_id, corner_counts) )

    infos.sort(reverse=True)
    return infos


def print_info(infos):
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


def shuffle_all(schedule):
    for matches in schedule:
        for teams in matches:
            random.shuffle(teams)


def print_schedule(writer, schedule):
    for matches in schedule:
        teams = map(str, chain.from_iterable(matches))
        print(helpers.SEPARATOR.join(teams), file=writer)


parser = argparse.ArgumentParser('Displays statistics about how often a team is in a given corner')
parser.add_argument('-i', '--ignore-ids', help='comma separated list of ids to ignore')
parser.add_argument('--fix', help='randomise corner assignment within each match and output a new schedule to the given file')
parser.add_argument('schedule_file', help='schedule to examine')

args = parser.parse_args()

#print("\n".join(lines))

ignores = map(int, args.ignore_ids.split(',')) if args.ignore_ids else []

schedule = load_schedule(args.schedule_file)
assert schedule, "Schedule file was empty!"

teams = convert(schedule, ignores)

infos = analyse(teams)
print_info(infos)

if not args.fix:
    exit()

shuffle_all(schedule)

with open(args.fix, 'w') as f:
    print_schedule(f, schedule)
