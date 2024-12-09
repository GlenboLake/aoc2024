import sys
import warnings
from collections import defaultdict
from itertools import combinations
from pprint import pprint
from typing import NamedTuple


class Vec2(NamedTuple):
    x: int
    y: int

    def __add__(self, other):
        if not isinstance(other, Vec2):
            warnings.warn(f'{other} is not a Vec2')
            return False
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        if not isinstance(other, Vec2):
            warnings.warn(f'{other} is not a Vec2')
        return Vec2(self.x - other.x, self.y - other.y)


class Antenna(NamedTuple):
    pos: Vec2
    value: str


def parse_input(filename):
    with open(filename) as f:
        text = f.read().splitlines()
    size = len(text)
    antennae = defaultdict(set)
    for r, line in enumerate(text):
        for c, char in enumerate(line):
            if char == '.':
                continue
            antennae[char].add(Vec2(r, c))
    return size, antennae


def part1(filename):
    size, antennae = parse_input(filename)

    antinodes: set[Vec2] = set()
    for antenna_group in antennae.values():
        for a, b in combinations(antenna_group, 2):
            diff = a - b
            antinodes.update({
                a + diff,
                b - diff
            })

    return len({
        an for an in antinodes
        if an.x in range(size) and an.y in range(size)
    })


def part2(filename):
    size, antennae = parse_input(filename)

    antinodes = {antenna for antenna_group in antennae.values() for antenna in antenna_group}
    for antenna_group in antennae.values():
        for a, b in combinations(antenna_group, 2):
            diff = a - b
            pos = a
            while pos.x in range(size) and pos.y in range(size):
                antinodes.add(pos)
                pos += diff
            pos = b
            while pos.x in range(size) and pos.y in range(size):
                antinodes.add(pos)
                pos -= diff
    return len(antinodes)


if __name__ == '__main__':
    assert part1('inputs/sample08.txt') == 14
    print('Part 1:', part1('inputs/day08.txt'))
    assert part2('inputs/sample08.txt') == 34
    print('Part 2:', part2('inputs/day08.txt'))
