#!/usr/bin/env python
import collections
import sys

if len(sys.argv) != 2 or '--help' in sys.argv:
    print 'Usage: faced.py <schedule-file>'
    print '  Displays statistics about which others a team have faced'
    exit(1)

matches = []
lines = [x.strip() for x in open(sys.argv[1])]
for line in lines:
    players = line.split('|')
    while len(players) > 4:
        matches.append(players[0:3])
        players = players[4:]
    matches.append(players[0:3])

c = collections.defaultdict(collections.Counter)

for match in matches:
    for tla in match:
        for faces in match:
            c[tla][faces] += 1

all_teams = set(c.keys())

for tla, opponents in c.iteritems():
    missed = all_teams - set(opponents.keys())
    del opponents[tla]
    all_repeats = {}
    faced = opponents.keys()
    for opp in faced:
        times = opponents[opp]
        if times > 1:
            all_repeats[opp] = times
