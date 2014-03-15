#!/usr/bin/env python
import collections
import sys
import copy
from functools import cmp_to_key

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

def calc_faced_in_game(game, container):
    for tla in game:
        for faces in game:
            container[tla][faces] += 1

def calc_faced_in_match(match, container):
    while len(match) > 4:
        calc_faced_in_game(match[0:4], container)
        match = match[4:]
    calc_faced_in_game(match, container)

# Calculate how many times each team faces each other, except in the selected
# match
cur_match_no = 0
for match in matches:
    if cur_match_no == int(sys.argv[2]):
        cur_match_no += 1
        continue

    calc_faced_in_match(match, c)
    cur_match_no += 1

all_teams = set(c.keys())

# Calculate a dictionary of how many times repeats happen: the size of the
# repeat maps to the number of times it happens. Due to an artifact of how
# this is counted, the "number of times" is twice as large as reality
def calc_scoring(sched):
    # Something involving defaults would be better, but requires thought
    output = dict()
    for i in range(len(matches)):
        output[i] = 0

    for tla, opponents in sched.iteritems():
        del opponents[tla]
        faced = opponents.keys()
        for opp in faced:
            times = opponents[opp]
            output[times] += 1

    # Remove repeats with zero count
    for i in output.keys():
        if output[i] == 0:
            del output[i]

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
    # Duplicate members?
    if len(set(comb)) != 4:
        continue

    comb = sorted(comb)
    astuple = (comb[0], comb[1], comb[2], comb[3])
    if astuple not in unique_games:
        unique_games.add(astuple)

# Combine the set of unique games into a set of matches. Guard against the same
# match but in a different order being found.
unique_matches = set()
for comb in product(unique_games, repeat=2):
    # Test that we actually have all 8 players playing in this match.
    g1p1, g1p2, g1p3, g1p4 = comb[0]
    g2p1, g2p2, g2p3, g2p4 = comb[1]
    if len(set([g1p1, g1p2, g1p3, g1p4, g2p1, g2p2, g2p3, g2p4])) != 8:
        continue

    g1 = comb[0]
    g2 = comb[1]
    if (g2, g1) in unique_matches:
        continue
    unique_matches.add((g1, g2))

# Now for some actual scoring. For each match, duplicate the scoring dictionary
# for the rest of the schedule, and add the generated match to that scoring.
scorelist = []
for m in unique_matches:
    g1, g2 = m
    g1p1, g1p2, g1p3, g1p4 = g1
    g2p1, g2p2, g2p3, g2p4 = g2

    sched = copy.deepcopy(c)
    calc_faced_in_match([g1p1, g1p2, g1p3, g1p4], sched)
    calc_faced_in_match([g2p1, g2p2, g2p3, g2p4], sched)
    score = calc_scoring(sched)

    scorelist.append((score, m))

def sortlist_cmp(x, y):
    # Project out the score, from the match
    xs, xm = x
    ys, ym = y
    return scoring_cmp(xs, ys)

scorelist = sorted(scorelist, key=cmp_to_key(sortlist_cmp))

for m in scorelist:
    score, match = m
    print "Match " + repr(match)
    print "  scored: " + repr(score)
