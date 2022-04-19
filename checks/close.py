import sys
from collections import Counter, defaultdict

import helpers

if len(sys.argv) != 2 or '--help' in sys.argv:
    print('Usage: close.py <schedule-file>')
    print('  Displays statistics about how close the matches for all teams are.')
    print('  A min-gap of 3 indicates that a team has a match, followed by two')
    print('  match intervals off, and then another match.')
    exit(1)

lines = helpers.load_lines(sys.argv[1])

matches = defaultdict(lambda: [])
breaks = defaultdict(lambda: [])

match_num = 1

for line in lines:
    teams = line.split('|')
    for tla in teams:
        matches[tla].append(int(match_num))

    match_num += 1

min_breaks = []

for tla, matches in matches.items():
    last_match = -25
    min_break = 200
    for match in matches:
        diff = match - last_match
        breaks[tla].append(diff)
        if diff < min_break:
            min_break = diff
        last_match = match
    min_breaks.append((tla, min_break, breaks[tla]))

print('Team\tMin-gap\tCount\tGaps')

count_n = 0
for tla, min_break, btla in sorted(min_breaks, key=lambda x: x[1]):
    c = Counter()
    for x in sorted(btla):
        c[x] += 1
    if min_break == 2:
        count_n += 1
    print(f"{tla}\t{min_break}\t{c[min_break]}\t{btla}")

print()
print(count_n)
