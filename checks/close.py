
from collections import defaultdict
import sys


lines = open(sys.argv[1], 'r').readlines()

matches = defaultdict(lambda: [])
breaks = defaultdict(lambda: [])

match_num = 1

for line in lines:
    teams = line.strip().split('|')
    for tla in teams:
        matches[tla].append(int(match_num))

    match_num += 1

min_breaks = []

for tla, matches in matches.iteritems():
    last_match = 1
    min_break = 200
    for match in matches:
        diff = match - last_match
        breaks[tla].append(diff)
        if diff < min_break:
            min_break = diff
        last_match = match
    min_breaks.append((tla, min_break, breaks[tla]))


for tla, min_break, btla in sorted(min_breaks, key=lambda x:x[1]):
    print "{0}\t{1}\t{2}".format(tla, min_break, btla)
