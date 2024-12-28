import os.path
from functools import lru_cache


@lru_cache
def next_secret(n):
    n = (n ^ (n*64)) % 16777216
    n = (n ^ (n//32)) % 16777216
    n = (n ^ (n*2048)) % 16777216
    return n

def get_nth_secret(num, n):
    for _ in range(n):
        num = next_secret(num)
    return num

def part1(data):
    if os.path.exists(data):
        with open(data) as f:
            data = f.read()
    return sum(get_nth_secret(int(num), 2000) for num in data.splitlines())

if __name__ == '__main__':
    assert part1('1\n10\n100\n2024') == 37327623
    print('Part 1:', part1('inputs/day22.txt'))