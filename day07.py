import time
from datetime import timedelta
from math import log10


def parse_input(filename):
    with open(filename) as f:
        for line in f:
            test_value, nums = line.split(': ')
            nums = nums.split()
            yield int(test_value), [int(n) for n in nums]


def part1(filename):
    def is_possible(test_value, nums):
        values = {nums[0]}
        for n in nums[1:]:
            values = {
                *[v + n for v in values],
                *[v * n for v in values],
            }
        return test_value in values

    return sum(test_value for test_value, nums in parse_input(filename) if is_possible(test_value, nums))


def part2(filename):
    def concat(a, b):
        mag = int(log10(b)) + 1
        return a * 10 ** mag + b

    def is_possible(test_value, nums):
        values = {nums[0]}
        for n in nums[1:]:
            values = {
                *[v + n for v in values],
                *[v * n for v in values],
                *[concat(v, n) for v in values],
            }
        return test_value in values

    return sum(test_value for test_value, nums in parse_input(filename) if is_possible(test_value, nums))


if __name__ == '__main__':
    assert part1('inputs/sample07.txt') == 3749
    print('Part 1:', part1('inputs/day07.txt'))
    assert part2('inputs/sample07.txt') == 11387
    start = time.time()
    print('Part 2:', part2('inputs/day07.txt'))
    end = time.time()
    print(f'Part 2 took {timedelta(seconds=end - start)}')
