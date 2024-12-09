from itertools import count, accumulate
from typing import NamedTuple


def part1(filename):
    with open(filename) as f:
        nums = map(int, f.read().strip())
    ids = count()
    disk = []
    file_id = None
    for n in nums:
        if file_id is None:
            file_id = next(ids)
        else:
            file_id = None
        disk.extend([file_id] * n)
    left = 0
    right = len(disk) - 1
    while left < right:
        if disk[right] is None:
            right -= 1
            continue
        if disk[left] is None:
            disk[left], disk[right] = disk[right], disk[left]
            right -= 1
        left += 1
    return sum(i * block for i, block in enumerate(disk) if block is not None)


class File:
    def __init__(self, id_: int, span: range = None):
        self.id = id_
        self.span = span

    @property
    def start(self):
        return self.span.start

    @property
    def stop(self):
        return self.span.stop

    def move_to(self, new_pos):
        self.span = range(new_pos, new_pos + len(self))

    def __len__(self):
        return len(self.span)

    def __str__(self):
        return f'<File {self.id} spanning ({self.start},{self.stop - 1})>'

    def checksum(self):
        return sum(self.id * n for n in self.span)


def part2(filename):
    with open(filename) as f:
        nums = list(map(int, f.read().strip()))

    def ids():
        i = count()
        while True:
            yield next(i)
            yield None

    file_ids = ids()

    indexes = accumulate([0, *nums])
    blocks = [File(next(file_ids), range(idx, idx + num)) for idx, num in zip(indexes, nums)]
    disk_size = blocks[-1].stop
    blocks = [b for b in blocks if b.id is not None]
    spans_to_check = range(blocks[-1].id, -1, -1)

    def find_free_space(size, max_pos) -> range | None:
        sorted_files = sorted([block.span for block in blocks] + [range(disk_size, disk_size)], key=lambda block: block.start)
        for a, b in zip(sorted_files, sorted_files[1:]):
            if a.stop > max_pos:
                break
            r = range(a.stop, b.start)
            if len(r) >= size:
                return r
        return None

    for file_id in spans_to_check:
        file = next(b for b in blocks if b.id == file_id)
        free_block = find_free_space(len(file), file.start - 1)
        if free_block is not None:
            file.span = range(free_block.start, free_block.start + len(file))
            continue
    return sum(block.checksum() for block in blocks)


if __name__ == '__main__':
    assert part1('inputs/sample09.txt') == 1928
    print('Part 1:', part1('inputs/day09.txt'))
    assert part2('inputs/sample09.txt') == 2858
    print('Part 2:', part2('inputs/day09.txt'))