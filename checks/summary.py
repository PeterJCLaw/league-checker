#!/usr/bin/env python3

import io
import argparse
import textwrap
import contextlib
from pathlib import Path

import close
import faced
import corners
import overlaps
import matches_per_team

CHECKS = [
    ("Closeness", close),
    ("Facings", faced),
    ("Corner allocations", corners),
    ("Matches per team", matches_per_team),
    ("Overlaps", overlaps),
]


def markdown_format(header: str, body: str) -> str:
    return f"## {header}\n\n{body}"


def github_collapsed_details_format(header: str, body: str) -> str:
    return textwrap.dedent("""
        <details>
        <summary>{header}</summary>

        ```
        {body}
        ```

        </details>
    """).format(
        # Separately format so that the dedent works as desired (`body` contains
        # non-indented content which otherwise causes dedenting not to happen)
        header=header,
        body=body.rstrip(),
    )


FORMATS = {
    'markdown': markdown_format,
    'github': github_collapsed_details_format,
}


def main(schedule_file: Path, formatter_slug: str) -> None:
    formatter = FORMATS[formatter_slug]

    for name, module in CHECKS:
        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            module.main(schedule_file)

        print(formatter(name, stdout.getvalue()))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Displays summary statistics about the given summary.",
    )
    parser.add_argument('schedule_file', type=Path, help="Schedule file to inspect")
    parser.add_argument(
        '--format',
        dest='formatter_slug',
        choices=FORMATS.keys(),
        default='markdown',
        help="Output format (default: %(default)s)",
    )
    return parser.parse_args()


if __name__ == '__main__':
    main(**parse_args().__dict__)
