import sys
import collections

if __name__ == "__main__":
    f = open(sys.argv[1]).read().split("\n")

    c = collections.Counter()

    for match in f:
        teams = match.split("|")
        for team in teams:
            c[team] += 1

    for line in c.most_common(300):
        print line
