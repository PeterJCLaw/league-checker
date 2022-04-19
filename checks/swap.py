import argparse
from pathlib import Path

import helpers


def main(schedule_file: Path, find: str, replace: str) -> None:
    lines = schedule_file.read_text().splitlines(keepends=False)

    find = find.upper()
    replace = replace.upper()

    for i, line in enumerate(lines):
        parts = line.strip().split(helpers.SEPARATOR)

        if find in parts and replace not in parts:
            print(parts)
            idx = parts.index(find)
            parts[idx] = replace
            print(parts)

            line = helpers.SEPARATOR.join(parts)
            lines[i] = line
            break

    schedule_file.write_text('\n'.join(lines))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=(
        "Searches for a match that contains the first entrant, but not the second"
        "and replaces the first for the second in that match."
    ))
    parser.add_argument('schedule_file', type=Path, help="File to search and modify")
    parser.add_argument('find', help="Entrant to search for")
    parser.add_argument('replace', help="Entrant to replace with")
    return parser.parse_args()


if __name__ == '__main__':
    main(**parse_args().__dict__)
