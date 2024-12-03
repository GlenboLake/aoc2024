import re


def part1(filename):
    with open(filename) as f:
        memory = f.read()
    max_match = re.compile(r'mul\((\d+),(\d+)\)')

    def evaluate(match: re.Match) -> int:
        return int(match.group(1)) * int(match.group(2))

    return sum(evaluate(match) for match in max_match.finditer(memory))

def part2(filename):
    with open(filename) as f:
        memory = f.read()

    pattern = re.compile(r"(?P<op>do|don't|mul)\((?:(?P<a>\d+),(?P<b>\d+))?\)")

    total = 0
    enabled = True
    for m in pattern.finditer(memory):
        match m.group('op'):
            case 'do':
                enabled=True
            case "don't":
                enabled=False
            case 'mul':
                if enabled:
                    total += int(m.group('a')) * int(m.group('b'))
    return total

def solve(filename):
    """Just for fun, solve them in tandem"""
    with open(filename) as f:
        memory = f.read()

    pattern = re.compile(r"(?P<op>do|don't|mul)\((?:(?P<a>\d+),(?P<b>\d+))?\)")
    sum1, sum2 = 0,0
    enabled = True

    for m in pattern.finditer(memory):
        match m.group('op'):
            case 'do':
                enabled=True
            case "don't":
                enabled=False
            case 'mul':
                value = int(m.group('a')) * int(m.group('b'))
                sum1 += value
                if enabled:
                    sum2 += value
    return sum1, sum2


if __name__ == '__main__':
    # assert part1('inputs/sample03a.txt') == 161
    # print('Part 1:', part1('inputs/day03.txt'))
    # assert part2('inputs/sample03b.txt') == 48
    # print('Part 2:', part2('inputs/day03.txt'))
    assert solve('inputs/sample03b.txt') == (161, 48)
    p1, p2 = solve('inputs/day03.txt')
    print('Part 1:', p1)
    print('Part 2:', p2)