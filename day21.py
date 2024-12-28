from collections import Counter, defaultdict
from collections.abc import Collection
from functools import lru_cache
from itertools import chain, pairwise, product
from animations import Point

type Keypad = dict[str, Point]

NUMERIC_KEYPAD = '''\
789
456
123
 0A
'''.rstrip()

DIRECTIONAL_KEYPAD = '''\
 ^A
<v>
'''.rstrip()


@lru_cache
def pad_to_points(pad: str) -> Keypad:
    """
    Take a string representation of a pad and cache a character-to-point mapping
    """
    return {
        ch: Point(x, y)
        for y, line in enumerate(pad.splitlines())
        for x, ch in enumerate(line)
        if not ch.isspace()
    }


@lru_cache
def simple_move(before: str, after: str, pad: str):
    """
    Get the sequence of button presses that will cause the next robot
    to go from one key to another, including the final A press
    """
    pad_points = pad_to_points(pad)
    before_coord = pad_points[before]
    after_coord = pad_points[after]
    dx = after_coord.x - before_coord.x
    dy = after_coord.y - before_coord.y
    return ''.join(chain(
        ('v' for _ in range(dy)),
        ('<' for _ in range(-dx)),
        ('>' for _ in range(dx)),
        ('^' for _ in range(-dy)),
    )) + 'A'


@lru_cache
def numpad_move(before: str, after: str):
    """
    Same as simple_move, but for the numpad
    """
    pad = pad_to_points(NUMERIC_KEYPAD)
    before_coord = pad[before]
    after_coord = pad[after]
    dx = after_coord.x - before_coord.x
    dx_text = ('>' if dx > 0 else '<') * abs(dx)
    dy = after_coord.y - before_coord.y
    dy_text = ('v' if dy > 0 else '^') * abs(dy)
    paths: set[str] = set()
    if (after_coord.x, before_coord.y) in pad.values():
        paths.add(dx_text + dy_text + 'A')
    if (before_coord.x, after_coord.y) in pad.values() and 0 not in (dx, dy):
        paths.add(dy_text + dx_text + 'A')
    return paths


# Cache all valid moves for the dir pad
dir_moves: dict[tuple[str, str], str] = {
    (before, after): simple_move(before, after, DIRECTIONAL_KEYPAD)
    for before in DIRECTIONAL_KEYPAD
    for after in DIRECTIONAL_KEYPAD
    if not before.isspace() and not after.isspace()
}

# A code such as <^A
type SequenceCounter = dict[tuple[str, str], int]


def expand_numpad(code: str) -> Collection[SequenceCounter]:
    """Get the sequence of button presses corresponding to the counted movements on the numpad"""
    stages = (numpad_move(a, b) for a, b in pairwise('A' + code))
    solutions = (''.join(bits) for bits in product(*stages))
    return [Counter(pairwise('A' + solution)) for solution in solutions]


def expand_dirpad(seq: SequenceCounter) -> SequenceCounter:
    """Get the sequence of button presses corresponding to the counted movements on the directional pad"""
    result: SequenceCounter = defaultdict(int)
    for pair, count in seq.items():
        subseq = dir_moves[pair]
        for a, b in pairwise('A' + subseq):
            result[a, b] += count
    return result


def solve(codes: list[str], num_robots: int) -> int:
    total = 0
    for code in codes:
        solutions = expand_numpad(code)
        for _ in range(num_robots):
            solutions = map(expand_dirpad, solutions)
        solutions = list(solutions)
        length = min(sum(s.values()) for s in solutions)
        num = int(code.rstrip('A').lstrip('0'))
        total += length * num
    return total


def part1(file):
    with open(file) as f:
        codes = f.read().splitlines()
    return solve(codes, 2)


def part2(file):
    with open(file) as f:
        codes = f.read().splitlines()
    return solve(codes, 25)


if __name__ == '__main__':
    assert part1('inputs/sample21.txt') == 126384
    print('Part 1:', part1('inputs/day21.txt'))
    print('Part 2:', part2('inputs/day21.txt'))
