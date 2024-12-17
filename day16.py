import sys
from collections import deque
from collections.abc import Collection
from enum import Enum

from animations import Point


class Facing(Point, Enum):
    N = Point(0, -1)
    S = Point(0, 1)
    E = Point(1, 0)
    W = Point(-1, 0)

    def right(self):
        x, y = self.value
        return Facing(Point(-y, x))

    def left(self):
        x, y = self.value
        return Facing(Point(y, -x))


def parse_input(filename):
    with open(filename) as f:
        maze = {
            Point(x, y): cell
            for y, row in enumerate(f)
            for x, cell in enumerate(row.rstrip())
            if cell in 'SE.'
        }
    start = [k for k, v in maze.items() if v == 'S'].pop()
    end = [k for k, v in maze.items() if v == 'E'].pop()
    return start, end, set(maze)


def part1(filename):
    start, end, maze = parse_input(filename)

    scores: dict[tuple[Point, Facing], int] = {}
    check: deque[tuple[Point, Facing, int]] = deque([(start, Facing.E, 0)])
    while check:
        pos, facing, score = check.popleft()
        if scores.get((pos, facing), sys.maxsize) <= score:
            continue
        scores[pos, facing] = score
        for new_pos, new_facing, new_score in [
            (pos + facing, facing, score + 1),
            (pos, facing.left(), score + 1000),
            (pos, facing.right(), score + 1000),
        ]:
            if pos + new_facing in maze and scores.get((new_pos, new_facing), sys.maxsize) > new_score:
                check.append((new_pos, new_facing, new_score))
    return min(s for (pos, _), s in scores.items() if pos == end)


def part2(filename):
    start, end, maze = parse_input(filename)
    type Path = Collection[Point]

    scores: dict[tuple[Point, Facing], tuple[int, list[Path]]] = {}
    check: deque[tuple[Point, Facing, int, Path]] = deque([(start, Facing.E, 0, {start})])
    while check:
        pos, facing, score, path = check.popleft()
        current_score, current_paths = scores.get((pos, facing), (sys.maxsize, []))
        if current_score < score:
            continue
        elif current_score == score:
            current_paths.append(path)
        else:
            scores[pos, facing] = score, [path]
        for new_pos, new_facing, new_score in [
            (pos + facing, facing, score + 1),
            (pos, facing.left(), score + 1000),
            (pos, facing.right(), score + 1000),
        ]:
            if pos + new_facing in maze and scores.get((new_pos, new_facing), (sys.maxsize, None))[0] > new_score:
                check.append((new_pos, new_facing, new_score, {*path, new_pos}))
    best_score = min(s for (pos, _), (s, _) in scores.items() if pos == end)
    paths = [p for (pos, _), (s, p) in scores.items() if pos == end and s == best_score]
    while not isinstance(paths[0], Point):
        paths = [p for path in paths for p in path]
    return len(set(paths))


if __name__ == '__main__':
    assert part1('inputs/sample16.txt') == 7036
    assert part1('inputs/sample16b.txt') == 11048
    print('Part 1:', part1('inputs/day16.txt'))
    assert part2('inputs/sample16.txt') == 45
    assert part2('inputs/sample16b.txt') == 64
    print('Part 2:', part2('inputs/day16.txt'))
