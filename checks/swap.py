import sys

if len(sys.argv) != 2 or '--help' in sys.argv:
    print('Usage: swap.py <schedule-file> <find-tla> <replace-tla>')
    print('  Searches for a match that contains the first team, but not the second')
    print('  and replaces the first for the second in that match.')
    exit(1)

f = open(sys.argv[1])
lines = f.read().split("\n")
f.close()

with open(sys.argv[1], 'w+') as f:

    for i in range(len(lines)):
        line = lines[i]
        parts = line.strip().split('|')

        find = sys.argv[2].upper()
        repl = sys.argv[3].upper()
        if find in parts and repl not in parts:
            print(parts)
            idx = parts.index(find)
            parts[idx] = repl
            print(parts)

            line = '|'.join(parts)
            lines[i] = line
            break

    text = "\n".join(lines)
    f.seek(0)
    f.write(text)
