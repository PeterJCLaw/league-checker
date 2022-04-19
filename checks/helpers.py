COMMENT_CHAR = '#'
SEPARATOR = '|'


def load_lines(file_path):
    lines = []
    with open(file_path, 'r') as f:
        for line in f.readlines():
            text = line.split(COMMENT_CHAR, 1)[0].strip()
            if text:
                lines.append(text)

    return lines
