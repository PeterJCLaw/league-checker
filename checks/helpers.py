from __future__ import annotations

import re
from typing import Tuple, Union
from pathlib import Path

HumanSortTuple = Tuple[Union[str, int], ...]

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
