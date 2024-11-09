from __future__ import annotations

import re
from typing import Tuple, Union, NewType
from pathlib import Path
from collections.abc import Sequence

HumanSortTuple = Tuple[Union[str, int], ...]

Team = NewType('Team', str)

Schedule = Sequence[Sequence[Team]]

COMMENT_CHAR = '#'
SEPARATOR = '|'


def load_lines(file_path: Path) -> list[str]:
    lines = []
    with open(file_path) as f:
        for line in f.readlines():
            text = line.split(COMMENT_CHAR, 1)[0].strip()
            if text:
                lines.append(text)

    return lines


def parse_schedule(lines: list[str]) -> Schedule:
    return [
        tuple(
            Team(t)
            for t in x.split(SEPARATOR)
        )
        for x in lines
    ]


def load_schedule(file_path: Path) -> Schedule:
    return parse_schedule(load_lines(file_path))


def human_sort_key(text: str) -> HumanSortTuple:
    """
    Split a string into text and numeric components so that they can be sorted
    in "human" order.
    """
    parts = re.findall(r'(\d+)', text)
    return tuple(
        int(x) if x.isdigit() else x
        for x in parts
    )
