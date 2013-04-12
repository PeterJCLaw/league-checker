
import sys

f = open(sys.argv[1])
lines = f.read().split("\n")
f.close()

with open(sys.argv[1], 'w+') as f:


    for i in range(len(lines)):
        line = lines[i]
        parts = line.strip().split('|')

        find = sys.argv[2].upper()
        if find in parts:
            idx = parts.index(find)
            parts[idx] = sys.argv[3].upper()

        line = '|'.join(parts)
        lines[i] = line
        break

    text = "\n".join(lines)
    f.seek(0)
    f.write(text)
