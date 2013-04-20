
import collections
import sys

if len(sys.argv) != 2 or '--help' in sys.argv:
    print 'Usage: faced.py <schedule-file>'
    print '  Displays statistics about which others a team have faced'
    exit(1)

matches = []
lines = [x.strip() for x in open(sys.argv[1])]
for line in lines:
    matches.append(line.split('|'))

c = collections.defaultdict(collections.Counter)

for match in matches:
    for tla in match:
        for faces in match:
            c[tla][faces] += 1

for tla, opponents in c.iteritems():
    opponents = opponents.keys()
    print '{0} faces {1} opponents: {2}'.format(tla, len(opponents), opponents)

