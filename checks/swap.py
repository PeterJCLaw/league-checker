
import sys

f = open(sys.argv[1])
lines = f.read().split("\n")
f.close()

with open(sys.argv[1], 'w+') as f:


    for i in range(len(lines)):
        line = lines[i]
        parts = line.strip().split('|')

        find = sys.argv[2].upper()
        repl = sys.argv[3].upper()
        if find in parts and not repl in parts:
            print parts
            idx = parts.index(find)
            parts[idx] = repl
            print parts

            line = '|'.join(parts)
            lines[i] = line
            break

    text = "\n".join(lines)
    f.seek(0)
    f.write(text)
