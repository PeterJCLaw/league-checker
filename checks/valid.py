
import sys

all_teams = [x.strip() for x in open('teams-2013', 'r').readlines()]

lines = open(sys.argv[1], 'r').readlines()

found_teams = []

for line in lines:
    teams = [x.strip() for x in line.strip().split('|')]
    assert len(set(teams)) == len(teams) == 4
    found_teams += teams

# Sanity
assert len(set(all_teams)) == len(all_teams)

# Sanity
missing_teams = set(all_teams) - set(found_teams)
print ', '.join(missing_teams)
assert len(set(found_teams)) == len(all_teams)

print 'Is valid'
