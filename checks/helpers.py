from typing import List
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
