import re
from typing import List, Tuple, Union
from pathlib import Path

COMMENT_CHAR = '#'
SEPARATOR = '|'


def load_lines(file_path: Path) -> List[str]:
    lines = []
    with open(file_path) as f:
        for line in f.readlines():
            text = line.split(COMMENT_CHAR, 1)[0].strip()
            if text:
                lines.append(text)

    return lines


def human_sort_key(text: str) -> Tuple[Union[str, int], ...]:
    """
    Split a string into text and numeric components so that they can be sorted
    in "human" order.
    """
    parts = re.findall('(\d+)', text)
    return tuple(
        int(x) if x.isdigit() else x
        for x in parts
    )
