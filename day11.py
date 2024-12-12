import time
from collections import Counter, defaultdict
from contextlib import contextmanager
from datetime import timedelta
from itertools import chain


def parse_input(filename):
    with open(filename) as f:
        return f.read().rstrip().split()


def blink(stones: list[str]):
    def blink_stone(stone):
        if stone == '0':
            return ['1']
        if len(stone) % 2 == 0:
            return [
                stone[:len(stone) // 2],
                stone[len(stone) // 2:].lstrip('0') or '0'
            ]
        return [str(int(stone) * 2024)]
    return list(chain.from_iterable(map(blink_stone, stones)))


def solve(filename, num_blinks):
    stones: dict[str, int] = Counter(parse_input(filename))
    for i in range(num_blinks):
        new_stones = defaultdict(int)
        for stone, count in stones.items():
            if stone == '0':
                new_stones['1'] += count
            elif len(stone) % 2 == 0:
                left = stone[:len(stone) // 2]
                right = stone[len(stone)//2:].lstrip('0') or '0'
                new_stones[left] += count
                new_stones[right] += count
            else:
                new_stones[str(int(stone)*2024)] += count
        stones = new_stones
    return sum(stones.values())


if __name__ == '__main__':
    assert solve('inputs/sample11.txt', 25) == 55312
    print('Part 1:', solve('inputs/day11.txt', 25))
    print('Part 2:', solve('inputs/day11.txt', 75))