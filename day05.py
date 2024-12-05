from collections import defaultdict, Counter
from typing import Collection, Mapping, Iterable, Sequence


def parse_input(filename: str) -> tuple[Mapping[int, Collection[int]], Iterable[Sequence[int]]]:
    with open(filename) as f:
        rule_text, update_text = f.read().split('\n\n')
    rules = {tuple(map(int, rule.split('|'))) for rule in rule_text.splitlines() if rule}
    ordering = defaultdict(set)
    for a, b in rules:
        ordering[a].add(b)
    updates = [
        tuple(map(int, update.split(',')))
        for update in update_text.splitlines()
        if update
    ]
    return ordering, updates


def is_ordered(ordering, update):
    for i, left in enumerate(update):
        for right in update[i + 1:]:
            if left in ordering[right]:
                return False
    return True


def part1(filename):
    ordering, updates = parse_input(filename)

    sorted_updates = [update for update in updates if is_ordered(ordering, update)]
    return sum(
        update[len(update) // 2]
        for update in sorted_updates
    )


def part2(filename):
    ordering, updates = parse_input(filename)

    unsorted_updates = [update for update in updates if not is_ordered(ordering, update)]

    def sort(update):
        nums = set(update)
        priority = Counter([
            a
            for a, bs in ordering.items()
            for b in bs
            if a in nums and b in nums
        ])
        return *sorted(priority, key=priority.get, reverse=True), *(nums - set(priority))

    return sum(
        sort(update)[len(update) // 2]
        for update in unsorted_updates
    )


if __name__ == '__main__':
    assert part1('inputs/sample05.txt') == 143
    print('Part 1:', part1('inputs/day05.txt'))
    assert part2('inputs/sample05.txt') == 123
    print('Part 2:', part2('inputs/day05.txt'))
