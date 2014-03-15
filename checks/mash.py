#!/usr/bin/env python
import collections
import sys

if len(sys.argv) != 3 or '--help' in sys.argv:
    print 'Usage: faced.py schedule-file matchno'
    print '  Displays statistics about which others a team have faced'
    exit(1)

matches = []
lines = [x.strip() for x in open(sys.argv[1])]
for line in lines:
    players = line.split('|')
    matches.append(players)

c = collections.defaultdict(collections.Counter)

def calc_faced_in_match(match, container):
    for tla in match:
        for faces in match:
            container[tla][faces] += 1

# Calculate how many times each team faces each other, except in the selected
# match
cur_match_no = 0
for match in matches:
    if cur_match_no == int(sys.argv[2]):
        continue

    calc_faced_in_match(match, c)
    cur_match_no += 1

all_teams = set(c.keys())

# Calculate a dictionary of how many times repeats happen: the size of the
# repeat maps to the number of times it happens. Due to an artifact of how
# this is counted, the "number of times" is twice as large as reality
def calc_scoring(c):
    output = collections.defaultdict(collections.Counter)

    for tla, opponents in c.iteritems():
        missed = all_teams - set(opponents.keys())
        del opponents[tla]
        all_repeats = {}
        faced = opponents.keys()
        for opp in faced:
            times = opponents[opp]
            output[times] += 1

    return output

# Define a comparator about the score a particular match configuration has.
# A 'better' score is one where the largest magnitude of repeat is less than
# another, i.e. a schedule with some 3-times repeats is better than one with
# any 4-time repeats.
# Failing that, the number of repeats is compared, in reducing magnitude, so
# a schedule with 20 3-time repeats is worse than one with 15 of them.
def scoring_cmp(x, y):
    xkeys = x.keys()
    ykeys = y.keys()

    if xkeys != ykeys:
        # One of these dicts has a higher magnitude of repeats than the other.
        xkeys = sorted(xkeys, reverse=True)
        ykeys = sorted(ykeys, reverse=True)

        # Find the highest magnitude of repeat
        highest = 0
        if xkeys[0] > ykeys[0]:
            highest = xkeys[0]
        else:
            highest = ykeys[0]

        # Decrease from there, finding where which schedule, x or y, has a
        # magnitude of repeat that the other doesn't
        for i in reversed(range(highest)):
            if i in xkeys and i not in ykeys:
                return 1
            elif i in ykeys and i not in xkeys:
                return -1
        return 0
    else:
        # The schedules have the same set of keys: compare the number of times
        # that each magnitude of repeats occurs
        xkeys = sorted(xkeys, reverse=True)
        for i in xkeys:
            if x[i] < y[i]:
                return -1
            elif x[i] > y[i]:
                return 1
        return 0

# Select the desired match
the_match = matches[int(sys.argv[2])]

# Now enumerate the set of unique matches that can be played with the teams
# in this match, re-ordered. Don't do anything fancy.

unique_games = set()

# Generate all possible 4-team combinations via generating all combinations,
# and canonicalising the order to avoid equivalent orderings being inserted.
from itertools import product
for comb in product(the_match, repeat=4):
    if len(comb) != 4:
        continue

    comb = sorted(comb)
    astuple = (comb[0], comb[1], comb[2], comb[3])
    unique_games.add(astuple)
print len(unique_games)
