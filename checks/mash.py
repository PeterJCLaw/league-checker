#!/usr/bin/env python3

import sys
import argparse
import itertools
import collections
from typing import (
    Set,
    Tuple,
    Counter,
    Mapping,
    Iterable,
    Sequence,
    FrozenSet,
    Collection,
    DefaultDict,
)
from functools import cmp_to_key

import helpers

ap = argparse.ArgumentParser(
    description="Identify teams that can be swapped between games inside matches",
)
ap.add_argument(
    "infile",
    help="Input schedule",
)
ap.add_argument(
    "matchno",
    type=int,
    help="Which match number to fiddle with",
)
ap.add_argument(
    "--auto-alter",
    action="store_true",
    help="Print the schedule with specified match patched",
)
ap.add_argument(
    "--multimatch",
    action="store_true",
    help="Consider swapping teams between this and the next match",
)
ap.add_argument(
    "--matches",
    type=int,
    default=0,
    help="Number of matches in each round",
)
ap.add_argument(
    "--closeness",
    type=int,
    default=0,
    help="Closeness criteria",
)

args = ap.parse_args()

if args.multimatch and (args.matches == 0 or args.closeness == 0):
    print("Matches and closeness options required for doing multimatch calcs", file=sys.stderr)
    sys.exit(1)

if args.multimatch and ((args.matchno + 1) % args.matches) == 0:
    print("Can't multi-match schedule over round boundaries, skipping this one", file=sys.stderr)
    args.multimatch = False

with open(args.infile) as f:
    lines = [x.strip() for x in f]

matches = [
    line.split(helpers.SEPARATOR)
    for line in lines
    if line and line[0] != helpers.COMMENT_CHAR
]

# Map TLA -> TLA -> count
facing_counts: DefaultDict[str, Counter[str]] = collections.defaultdict(collections.Counter)


def calc_faced_in_game(
    game: Collection[str],
    container: DefaultDict[str, Counter[str]],
    sub: bool,
) -> None:
    for tla in game:
        for faces in game:
            if sub:
                container[tla][faces] -= 1
            else:
                container[tla][faces] += 1


def calc_faced_in_match(
    match: Sequence[str],
    container: DefaultDict[str, Counter[str]],
    sub: bool = False,
) -> None:
    while len(match) > 4:
        calc_faced_in_game(match[0:4], container, sub)
        match = match[4:]
    calc_faced_in_game(match, container, sub)


# Calculate how many times each team faces each other, except in the selected
# match
cur_match_no = 0
forward_matches = []
middle_idx = 0
for match in matches:
    if cur_match_no == args.matchno:
        cur_match_no += 1
        continue
    elif args.multimatch and cur_match_no == args.matchno + 1:
        # Store earlier matches for checking closeness criteria
        middle_idx = cur_match_no - 1
        firstidx = max(0, middle_idx - args.closeness)
        forward_matches = matches[firstidx:middle_idx]

        cur_match_no += 1
        continue

    calc_faced_in_match(match, facing_counts)
    cur_match_no += 1

num_after_matches = min(middle_idx + 2 + args.closeness, len(matches))
after_matches = matches[middle_idx + 2:num_after_matches]

# Calculate the teams who'll conflict with players in our matches in multimatch
# mode

forward_teams = frozenset(itertools.chain.from_iterable(forward_matches))
after_teams = frozenset(itertools.chain.from_iterable(after_matches))

all_teams = set(facing_counts.keys())


def calc_scoring(sched: DefaultDict[str, Counter[str]]) -> Mapping[int, int]:
    """
    Calculate a dictionary of how many times repeats happen: the size of the
    repeat maps to the number of times it happens. Due to an artifact of how
    this is counted, the "number of times" is twice as large as reality
    """
    # Something involving defaults would be better, but requires thought
    output = dict.fromkeys(range(len(matches)), 0)

    for tla, opponents in sched.items():
        del opponents[tla]
        faced = opponents.keys()
        for opp in faced:
            times = opponents[opp]
            if times == 0:
                continue

            output[times] += 1

    # Remove repeats with zero count
    for i in list(output.keys()):
        if output[i] == 0:
            del output[i]

    return output


def scoring_cmp(x: Mapping[int, int], y: Mapping[int, int]) -> int:
    """
    Define a comparator about the score a particular match configuration has.
    A 'better' score is one where the largest magnitude of repeat is less than
    another, i.e. a schedule with some 3-times repeats is better than one with
    any 4-time repeats.
    Failing that, the number of repeats is compared, in reducing magnitude, so
    a schedule with 20 3-time repeats is worse than one with 15 of them.
    """
    xkeys: Collection[int] = x.keys()
    ykeys: Collection[int] = y.keys()

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
        for i in reversed(range(highest + 1)):
            if i in xkeys and i not in ykeys:
                return -1
            elif i in ykeys and i not in xkeys:
                return 1
        return 0
    else:
        # The schedules have the same set of keys: compare the number of times
        # that each magnitude of repeats occurs
        xkeys = sorted(xkeys, reverse=True)
        for i in xkeys:
            if x[i] < y[i]:
                return 1
            elif x[i] > y[i]:
                return -1
        return 0


# Select the desired match
the_teams = matches[int(args.matchno)]
first_match = frozenset(the_teams)
if args.multimatch:
    the_teams = the_teams + matches[args.matchno + 1]

# Now enumerate the set of unique matches that can be played with the teams
# in this match, re-ordered. Don't do anything fancy.


def get_unique_games(teams: Iterable[str]) -> Set[FrozenSet[str]]:
    """
    Generate all possible 4-team combinations via generating all combinations,
    and canonicalising the order to avoid equivalent orderings being inserted.
    """
    unique_games = set()

    for comb in itertools.product(the_teams, repeat=4):
        # Duplicate members?
        theset = frozenset(comb)
        if len(theset) != 4:
            continue

        if theset not in unique_games:
            unique_games.add(theset)

    return unique_games


unique_games = get_unique_games(the_teams)


def get_unique_matches(
    unique_games: Set[FrozenSet[str]],
    multimatch: bool,
) -> Set[Tuple[FrozenSet[str], FrozenSet[str]]]:
    """
    Combine the set of unique games into a set of matches. Guard against the same
    match but in a different order being found.
    """

    unique_matches = set()
    for g1, g2 in itertools.product(unique_games, repeat=2):
        # Test that we actually have all 8 players playing in this match.
        if not g1.isdisjoint(g2):
            continue

        # In multimatch mode, check that the match is either a completely unchanged
        # set of teams from either match, or only has one team difference. This
        # means we only explore one pair of teams swapping matches, keeping the size
        # of exploration feasible.
        if multimatch:
            both = g1 | g2
            inter_first = both & first_match

            thelen = len(inter_first)
            if thelen != 0 and thelen != 1 and thelen != 7 and thelen != 8:
                continue

        if (g2, g1) in unique_matches:
            continue
        unique_matches.add((g1, g2))

    return unique_matches


unique_matches = get_unique_matches(unique_games, args.multimatch)


# In multimatch mode, turn the unique matches set into a set of match pairs.
match_pairs = set()
if args.multimatch:
    for comb in itertools.product(unique_matches, repeat=2):
        m1, m2 = comb
        set1, set2 = m1
        set3, set4 = m2
        if len(set1 | set2 | set3 | set4) != 16:
            continue

        # That's checked uniqueness. Now look for closeness hazards.
        if len(set3 & after_teams) != 0:
            continue
        if len(set4 & after_teams) != 0:
            continue
        if len(set1 & forward_teams) != 0:
            continue
        if len(set2 & forward_teams) != 0:
            continue

        match_pairs.add(comb)

# Now for some actual scoring. For each match, duplicate the scoring dictionary
# for the rest of the schedule, and add the generated match to that scoring.


def add_generated_match_sched(
    m: Tuple[Iterable[str], Iterable[str]],
    sched: DefaultDict[str, Counter[str]],
    sub: bool,
) -> DefaultDict[str, Counter[str]]:
    g1, g2 = m

    calc_faced_in_match(list(g1), sched, sub)
    calc_faced_in_match(list(g2), sched, sub)
    return sched


scorelist = []
if not args.multimatch:
    for m in unique_matches:
        sched = facing_counts
        sched = add_generated_match_sched(m, sched, False)
        score = calc_scoring(sched)
        sched = add_generated_match_sched(m, sched, True)

        scorelist.append((score, m))
else:
    for m1, m2 in match_pairs:
        sched = facing_counts
        sched = add_generated_match_sched(m1, sched, False)
        sched = add_generated_match_sched(m2, sched, False)
        score = calc_scoring(sched)

        sched = add_generated_match_sched(m1, sched, True)
        sched = add_generated_match_sched(m2, sched, True)
        facing_counts = sched

        scorelist.append((score, (m1, m2)))  # type: ignore[arg-type]


def sortlist_cmp(x, y):
    # Project out the score, from the match
    x_score, x_match = x
    y_score, y_match = y
    return scoring_cmp(x_score, y_score)


scorelist = [max(scorelist, key=cmp_to_key(sortlist_cmp))]


class bcolours:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


if not args.auto_alter:
    if not args.multimatch:
        for score, (g1, g2) in scorelist:
            plist = list(g1)
            plist += list(g2)
            normalised = "|".join(plist)

            print("Match " + bcolours.OKGREEN + repr((g1, g2)) + bcolours.ENDC)
            print("  normalised as " + bcolours.OKBLUE + normalised + bcolours.ENDC)
            print("  scored: " + bcolours.FAIL + repr(score) + bcolours.ENDC)
    else:
        for score, (match1, match2) in scorelist:
            m1g1, m1g2 = match1
            m2g1, m2g2 = match2
            plist = list(m1g1)
            plist += list(m1g2)
            normalised1 = "|".join(plist)
            plist = list(m2g1)
            plist += list(m2g2)
            normalised2 = "|".join(plist)

            print("Match " + bcolours.OKGREEN + repr(match1) + bcolours.ENDC)
            print("      " + bcolours.OKGREEN + repr(match2) + bcolours.ENDC)
            print("  normalised as " + bcolours.OKBLUE + normalised1 + bcolours.ENDC)
            print("                " + bcolours.OKBLUE + normalised2 + bcolours.ENDC)
            print("  scored: " + bcolours.FAIL + repr(score) + bcolours.ENDC)

    sys.exit(0)

# Auto alter is enabled: re-read the input file, printing out every line
# except the desired match, replacing it with the optimal match found.

cur_match_no = 0
for line in lines:
    if len(line) > 0 and line[0] == helpers.COMMENT_CHAR:
        print(line)
        continue

    if cur_match_no == args.matchno:
        # Replace it. Pick the optimal ordering, which is the last in the list
        bestscore, bestmatch = scorelist[-1]

        if not args.multimatch:
            g1, g2 = bestmatch
            plist = list(g1)
            plist += list(g2)
            print(helpers.SEPARATOR.join(plist))
        else:
            (g1, g2), (g3, g4) = bestmatch  # type: ignore[assignment]
            plist = list(g1)
            plist += list(g2)
            print(helpers.SEPARATOR.join(plist))
            plist = list(g3)
            plist += list(g4)
            print(helpers.SEPARATOR.join(plist))
    elif args.multimatch and cur_match_no == args.matchno + 1:
        pass  # already printed it
    else:
        # Just print it
        print(line)

    cur_match_no += 1
