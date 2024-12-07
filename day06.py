from typing import NamedTuple

EMPTY = '.'
OBSTACLE = '#'
GUARD = '^'


class Vec2(NamedTuple):
    r: int
    c: int

    def __add__(self, other):
        assert isinstance(other, Vec2)
        return Vec2(self.r + other.r, self.c + other.c)


def parse_input(filename):
    with open(filename) as f:
        grid = f.read().rstrip().splitlines()
    obstacles = set()
    start_pos = Vec2(-1, -1)
    for r, line in enumerate(grid):
        for c, char in enumerate(line):
            if char == OBSTACLE:
                obstacles.add(Vec2(r, c))
            elif char == GUARD:
                start_pos = Vec2(r, c)
    grid_size = Vec2(len(grid), len(grid[0]))
    return grid_size, obstacles, start_pos


def simulate(grid_size: Vec2, obstacles: set[Vec2], guard: Vec2):
    def guard_in_grid():
        return 0 <= guard.r < grid_size.r and 0 <= guard.c < grid_size.c

    def peek():
        return guard + movement

    def turn():
        nonlocal movement
        movement = Vec2(movement.c, -movement.r)

    movement = Vec2(-1, 0)
    history = {(guard, movement)}
    while True:
        if (new_pos := peek()) in obstacles:
            turn()
            history.add((guard, movement))
        else:
            guard = new_pos
            if guard_in_grid():
                if (guard, movement) in history:
                    return None
                history.add((guard, movement))
            else:
                return len({pos for pos, facing in history})


def part1(filename):
    return simulate(*parse_input(filename))


def part2(filename):
    # TODO: Try to analyze path instead
    grid_size, obstacles, start_pos = parse_input(filename)
    invalid = (*obstacles, start_pos)
    total = 0
    for r in range(grid_size.r):
        for c in range(grid_size.c):
            if (r, c) in invalid:
                continue
            if simulate(grid_size, obstacles | {Vec2(r,c)}, start_pos) is None:
                total += 1
        print(f'Row {r} complete, {total=}')
    return total


if __name__ == '__main__':
    assert part1('inputs/sample06.txt') == 41
    print('Part 1:', part1('inputs/day06.txt'))
    assert part2('inputs/sample06.txt') == 6
    print('Part 2:', part2('inputs/day06.txt'))
