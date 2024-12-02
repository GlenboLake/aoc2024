def parse_input(filename):
    with open(filename) as f:
        for line in f.read().splitlines():
            yield [int(x) for x in line.split()]


def check_safe(levels):
    changes = {a - b for a, b in zip(levels, levels[1:])}
    return changes <= {1, 2, 3} or changes <= {-1, -2, -3}


def part1(filename):
    safe = 0
    for levels in parse_input(filename):
        if check_safe(levels):
            safe += 1
    return safe


def part2(filename):
    safe = 0
    for levels in parse_input(filename):
        if check_safe(levels):
            safe += 1
            continue
        for i in range(len(levels)):
            if check_safe(levels[:i] + levels[i + 1:]):
                safe += 1
                break
    return safe


if __name__ == '__main__':
    assert part1('inputs/sample02.txt') == 2
    print('Part 1:', part1('inputs/day02.txt'))
    assert part2('inputs/sample02.txt') == 4
    print('Part 2:', part2('inputs/day02.txt'))
