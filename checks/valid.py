
import sys

lines = open(sys.argv[1], 'r').readlines()

for line in lines:
    teams = line.strip().split('|')
    assert len(set(teams)) == len(teams) == 4

print 'Is valid'
