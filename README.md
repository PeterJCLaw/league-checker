# League Checker

[![CircleCI](https://circleci.com/gh/PeterJCLaw/league-checker/tree/main.svg?style=svg)](https://circleci.com/gh/PeterJCLaw/league-checker/tree/main)

Checks for a schedule of league matches.

These checks are extracted from https://github.com/PeterJCLaw/match-scheduler.

## Schedule format

The expected format for a schedule file is one match per line, entrants
separated by pipes (`|`). Comments are started with hashes (`#`). Empty lines
and whitespace around entrants are ignored.

Typically entrants are specified as numbers so that the schedules are agnostic
of the actual competitors. (For any fair non-seeded schedule it should always be
possible to assign any entrant id to any competitor anyway).

For example:

``` plain
# This is a comment
1|3|22|0
13|2|6|9 # This is also a comment
10|14|3|7
```

## Checks

A summary of the most common checks can be obtained by running:

``` shell
./checks/summary.py path/to/schedule.txt
```

See the help messages of each check command for details.
