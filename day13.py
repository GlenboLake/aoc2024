import re
from pprint import pprint
from typing import NamedTuple, Literal


class Point(NamedTuple):
    x: int
    y: int

    @property
    def slope(self):
        return self.y / self.x


class Machine(NamedTuple):
    a: Point
    b: Point
    prize: Point

    @property
    def cost(self):
        """
        Number of A-presses: na
        Number of B-presses: nb
        na * a.x + nb * b.x = prize.x
        na * a.y + nb * b.y = prize.y

        [ax  bx  px]
        [ay  by  py]
        
        The RREF of this matrix gives:
        A-presses: (by*px-bx*py)/(ax*by-bx*ay)
        B-presses: (ax*py-ay*px)/(ax*by-ay*bx)
        """
        ax, ay = self.a
        bx, by = self.b
        px, py = self.prize
        a_presses = (by * px - bx * py) / (ax * by - bx * ay)
        b_presses = (ax * py - ay * px) / (ax * by - ay * bx)
        if a_presses == int(a_presses) and b_presses == int(b_presses):
            return int(3 * a_presses + b_presses)
        return 0


def parse_input(filename, part: Literal[1, 2]):
    button = re.compile(r'Button [AB]: X\+(?P<x>\d+), Y\+(?P<y>\d+)')
    prize = re.compile(r'Prize: X=(?P<x>\d+), Y=(?P<y>\d+)')
    with open(filename) as f:
        machine_texts = f.read().split('\n\n')
    machines = []
    for i, machine in enumerate(machine_texts):
        a, b, p = machine.splitlines()
        a_button = Point(**{k: int(v) for k, v in button.fullmatch(a).groupdict().items()})
        b_button = Point(**{k: int(v) for k, v in button.fullmatch(b).groupdict().items()})
        prize_loc = {k: int(v) for k, v in prize.fullmatch(p).groupdict().items()}
        if part == 2:
            prize_loc = {k: v + 10000000000000 for k, v in prize_loc.items()}
        machines.append(Machine(a_button, b_button, Point(**prize_loc)))
    return machines


def part1(filename):
    machines = parse_input(filename, 1)
    return sum(machine.cost for machine in machines)


def part2(filename):
    machines = parse_input(filename, 2)
    return sum(machine.cost for machine in machines)


if __name__ == '__main__':
    assert part1('inputs/sample13.txt') == 480
    print('Part 1:', part1('inputs/day13.txt'))
    print('Part 2:', part2('inputs/day13.txt'))
