from collections import Counter


def parse_input(filename):
    with open(filename) as f:
        pairs = (
            map(int, line.split())
            for line in f.read().splitlines()
        )
        return tuple(zip(*pairs))


def part1(filename):
    left, right = parse_input(filename)
    return sum(
        abs(l - r) for l, r in zip(sorted(left), sorted(right))
    )


def part2(filename):
    left, right = parse_input(filename)
    freq = Counter(right)
    return sum(
        num * freq[num]
        for num in left
    )


if __name__ == '__main__':
    assert part1('sample01.txt') == 11
    print('Part 1:', part1('day01.txt'))
    assert part2('sample01.txt') == 31
    print('Part 2:', part2('day01.txt'))
