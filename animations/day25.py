import itertools
from itertools import batched


def parse(filename):
    locks = []
    keys = []

    def parse_key(key):
        lines = [line.strip() for line in key if not line.isspace()]
        pins = [pin.count('#')-1 for pin in zip(*lines)]
        if key[0][0] == '#':
            locks.append(pins)
        else:
            keys.append(pins)

    with open(filename) as f:
        for batch in batched(f, 8):
            parse_key(batch)
    return locks, keys


def solve(filename):
    locks, keys = parse(filename)

    def fits(lock, key):
        return all(l + k <= 5 for l,k in zip(lock, key))
    return sum(1 for lock, key in itertools.product(locks, keys) if fits(lock, key))


if __name__ == '__main__':
    assert solve('../inputs/sample25.txt') == 3
    print(solve('../inputs/day25.txt'))
