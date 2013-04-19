
import collections
import sys

if __name__ == "__main__":

    if len(sys.argv) != 2 or '--help' in sys.argv:
        print 'Usage: pound.py <schedule-file>'
        print '  Prints the number of matches each team has, sorted by match count'
        exit(1)

    f = open(sys.argv[1]).read().split("\n")

    c = collections.Counter()

    for match in f:
        teams = match.split("|")
        for team in teams:
            c[team] += 1

    for line in c.most_common(300):
        print line
